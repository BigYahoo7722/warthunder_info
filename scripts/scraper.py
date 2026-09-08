#!/usr/bin/env python3
"""
scraper.py — War Thunder Codex data pipeline
==============================================

NOT AFFILIATED WITH OR ENDORSED BY GAIJIN ENTERTAINMENT. "War Thunder" is a
trademark of Gaijin Entertainment. This is a personal/fan-project data tool
in the same spirit as the public community projects it's modeled on
(gszabi99/War-Thunder-Datamine, Sgambe33/WarThunder-Vehicles-API,
Ultra119/WTMETACenter). Before a real run: read Gaijin's Terms of Service,
check the target site's /robots.txt, and don't hammer either source — the
rate limiting below is load-bearing, not decorative.

Two independent extractors, because the two sources are good at different
things:

  WikiExtractor
      Pulls page text/infobox data from the community-run, CC-BY-SA
      licensed War Thunder wiki on Fandom (warthunder.fandom.com) via the
      standard MediaWiki API. Good for names, categories, short
      descriptions, "how to obtain" notes. NOTE: Gaijin's own
      wiki.warthunder.com was relaunched as a custom-built "Wiki 3.0" site
      (dark theme, dynamic layout) rather than a MediaWiki install, so it
      needs a different, HTML-based extractor (WikiExtractor.scrape_official_html
      is stubbed for this — confirm current DOM structure before relying on
      it, and note it's Gaijin's own first-party property, so hold it to a
      stricter ToS reading than the Fandom mirror).

  DatamineExtractor
      Walks a local clone of gszabi99/War-Thunder-Datamine
      (github.com/gszabi99/War-Thunder-Datamine), which unpacks the game
      client's own unit definitions to readable JSON. Despite the .blkx
      extension these files ARE plain JSON — confirmed directly against
      aces.vromfs.bin_u/gamedata/units/tankmodels/germ_leopard_2a5.blkx.
      Good for exact mass, speed, turn rate, and per-zone armor thickness —
      the actual numbers the client uses, not a paraphrase of them.

merge_sources() reconciles the two into the Vehicle shape defined in
lib/types.ts, preferring datamine numbers wherever both sources have one.

Honesty note on scope: the ground-vehicle datamine parser below is written
against a real sample file and its exact field names. The aircraft/ship
branch is written from the same repo's evident folder convention
(gamedata/units/<type>/...) but WITHOUT a confirmed sample file — the
environment that generated this script has network egress restricted to
package registries, not general GitHub browsing at the time that branch was
written. It's marked NEEDS VERIFICATION below rather than presented with
false confidence. Same for crew count — see the comment in
_extract_crew_count for why a naive key-count is wrong and what to use
instead.

Usage:
    # 1. Wiki pass (Fandom mirror, MediaWiki API)
    python3 scraper.py wiki --nation usa --category army --out data/raw_wiki_usa_army.json

    # 2. Datamine pass (sparse-clones the repo if --repo-path doesn't exist)
    python3 scraper.py datamine --repo-path ./War-Thunder-Datamine --out data/raw_datamine.json

    # 3. Merge into the shape the Next.js app expects
    python3 scraper.py merge --wiki data/raw_wiki_usa_army.json \\
                              --datamine data/raw_datamine.json \\
                              --out data/vehicles.json
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
import urllib.robotparser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator, Optional
from urllib.parse import urljoin

try:
    import requests
except ImportError:  # pragma: no cover
    sys.exit("Missing dependency: pip install requests beautifulsoup4 --break-system-packages")

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    sys.exit("Missing dependency: pip install requests beautifulsoup4 --break-system-packages")


logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s  %(message)s")
log = logging.getLogger("wt-codex-scraper")

USER_AGENT = (
    "war-thunder-codex-scraper/0.1 "
    "(personal fan-project data pipeline; contact: set-your-email-here)"
)
REQUEST_DELAY_SEC = 1.5  # minimum gap between requests to the SAME host
FANDOM_API = "https://warthunder.fandom.com/api.php"
DATAMINE_REPO = "https://github.com/gszabi99/War-Thunder-Datamine.git"


# ---------------------------------------------------------------------------
# Shared HTTP plumbing: one polite session per host, robots.txt-aware.
# ---------------------------------------------------------------------------

class PoliteSession:
    """A requests.Session that checks robots.txt once per host and enforces
    a minimum delay between requests. Not a full scheduler — good enough for
    a single-process scraper run."""

    def __init__(self, user_agent: str = USER_AGENT, delay: float = REQUEST_DELAY_SEC):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = user_agent
        self.delay = delay
        self._last_request_at: dict[str, float] = {}
        self._robots: dict[str, urllib.robotparser.RobotFileParser] = {}

    def _robots_for(self, url: str) -> urllib.robotparser.RobotFileParser:
        host = urljoin(url, "/")
        if host not in self._robots:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(urljoin(host, "/robots.txt"))
            try:
                rp.read()
            except Exception as exc:  # noqa: BLE001 — robots.txt fetch failing shouldn't crash the run
                log.warning("Could not read robots.txt for %s (%s); proceeding cautiously", host, exc)
            self._robots[host] = rp
        return self._robots[host]

    def get(self, url: str, **kwargs) -> requests.Response:
        rp = self._robots_for(url)
        if not rp.can_fetch(self.session.headers["User-Agent"], url):
            raise PermissionError(f"robots.txt disallows fetching {url}")

        host = urljoin(url, "/")
        elapsed = time.monotonic() - self._last_request_at.get(host, 0)
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

        resp = self.session.get(url, timeout=20, **kwargs)
        self._last_request_at[host] = time.monotonic()
        resp.raise_for_status()
        return resp


# ---------------------------------------------------------------------------
# Wiki extractor (Fandom mirror — CC-BY-SA, standard MediaWiki API)
# ---------------------------------------------------------------------------

NATION_TO_WIKI_CATEGORY = {
    # Fandom category names as of this script's writing — MediaWiki category
    # names are case/underscore-sensitive; verify against
    # https://warthunder.fandom.com/wiki/Special:Categories before a real run.
    "usa": "USA",
    "germany": "Germany",
    "ussr": "USSR",
    "britain": "Great_Britain",
    "japan": "Japan",
    "china": "China",
    "italy": "Italy",
    "france": "France",
    "sweden": "Sweden",
    "israel": "Israel",
}
CATEGORY_TO_WIKI_SUFFIX = {
    "aviation": "aircraft",
    "army": "ground_vehicles",
    "fleet": "ships",
    "helicopters": "helicopters",
}


class WikiExtractor:
    def __init__(self, session: Optional[PoliteSession] = None):
        self.http = session or PoliteSession()

    def get_category_members(self, category: str, limit: int = 500) -> list[str]:
        """Return page titles in a MediaWiki category, following continuation."""
        titles: list[str] = []
        cmcontinue = None
        while True:
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Category:{category}",
                "cmlimit": min(limit, 500),
                "format": "json",
            }
            if cmcontinue:
                params["cmcontinue"] = cmcontinue

            resp = self.http.get(FANDOM_API, params=params)
            data = resp.json()
            members = data.get("query", {}).get("categorymembers", [])
            titles.extend(m["title"] for m in members)

            cmcontinue = data.get("continue", {}).get("cmcontinue")
            if not cmcontinue or len(titles) >= limit:
                break
        return titles[:limit]

    def get_page_html(self, title: str) -> str:
        params = {"action": "parse", "page": title, "prop": "text", "format": "json"}
        resp = self.http.get(FANDOM_API, params=params)
        data = resp.json()
        return data.get("parse", {}).get("text", {}).get("*", "")

    def extract_infobox(self, html: str) -> dict[str, str]:
        """Best-effort key/value pull from the page's infobox table. Fandom's
        infobox markup varies by wiki skin/template, so this looks for the
        common `.portable-infobox` (modern Fandom) shape first and falls back
        to any definition-list-style table. Always verify against a live
        page — infobox templates get redesigned."""
        soup = BeautifulSoup(html, "html.parser")
        out: dict[str, str] = {}

        infobox = soup.select_one(".portable-infobox")
        if infobox:
            for item in infobox.select(".pi-item"):
                label_el = item.select_one(".pi-data-label")
                value_el = item.select_one(".pi-data-value")
                if label_el and value_el:
                    out[label_el.get_text(strip=True)] = value_el.get_text(" ", strip=True)
            return out

        # Fallback: generic infobox table (older skin)
        table = soup.select_one("table.infobox")
        if table:
            for row in table.select("tr"):
                cells = row.find_all(["th", "td"])
                if len(cells) == 2:
                    out[cells[0].get_text(strip=True)] = cells[1].get_text(" ", strip=True)
        return out

    def extract_nation_category(self, nation: str, category: str, limit: int = 200) -> list[dict]:
        wiki_nation = NATION_TO_WIKI_CATEGORY.get(nation)
        wiki_suffix = CATEGORY_TO_WIKI_SUFFIX.get(category)
        if not wiki_nation or not wiki_suffix:
            raise ValueError(f"Unknown nation/category combination: {nation}/{category}")

        wiki_category = f"{wiki_nation}_{wiki_suffix}"
        log.info("Fetching category members: %s", wiki_category)
        titles = self.get_category_members(wiki_category, limit=limit)
        log.info("Found %d pages in %s", len(titles), wiki_category)

        records = []
        for i, title in enumerate(titles, 1):
            log.info("[%d/%d] %s", i, len(titles), title)
            html = self.get_page_html(title)
            infobox = self.extract_infobox(html)
            records.append({
                "name": title,
                "nation": nation,
                "category": category,
                "wiki_infobox_raw": infobox,  # merge_sources() maps this loosely; see that function
            })
        return records

    def scrape_official_html(self, vehicle_slug: str) -> dict:
        """STUB — wiki.warthunder.com ("Wiki 3.0") is a custom-built site, not
        MediaWiki, so it needs its own selectors once you've inspected a live
        page (view-source, or your browser devtools' Elements panel). This
        function intentionally raises rather than guessing a DOM shape that
        was never confirmed."""
        raise NotImplementedError(
            "Inspect a live page on wiki.warthunder.com and fill in real "
            "selectors before using this path — see module docstring."
        )


# ---------------------------------------------------------------------------
# Datamine extractor (gszabi99/War-Thunder-Datamine — plain JSON despite
# the .blkx extension)
# ---------------------------------------------------------------------------

class DatamineExtractor:
    UNITS_SUBPATH = "aces.vromfs.bin_u/gamedata/units"

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    @classmethod
    def ensure_repo(cls, repo_path: Path, clone_if_missing: bool = True) -> "DatamineExtractor":
        units_dir = repo_path / cls.UNITS_SUBPATH
        if units_dir.exists():
            return cls(repo_path)
        if not clone_if_missing:
            raise FileNotFoundError(f"{units_dir} not found and clone_if_missing=False")

        log.info("Sparse-cloning %s → %s (units/ subtree only)", DATAMINE_REPO, repo_path)
        # The full repo is a dump of the entire game client's data files —
        # sparse checkout keeps this to just the unit definitions we need
        # instead of pulling everything.
        repo_path.mkdir(parents=True, exist_ok=True)
        run = lambda *cmd: subprocess.run(cmd, cwd=repo_path, check=True)  # noqa: E731
        run("git", "init", "-q")
        run("git", "remote", "add", "origin", DATAMINE_REPO)
        run("git", "config", "core.sparseCheckout", "true")
        sparse_file = repo_path / ".git" / "info" / "sparse-checkout"
        sparse_file.parent.mkdir(parents=True, exist_ok=True)
        sparse_file.write_text(f"{cls.UNITS_SUBPATH}/*\n")
        run("git", "fetch", "--depth", "1", "origin", "master")
        run("git", "checkout", "master")
        return cls(repo_path)

    def iter_unit_files(self) -> Iterator[Path]:
        units_dir = self.repo_path / self.UNITS_SUBPATH
        yield from units_dir.rglob("*.blkx")

    @staticmethod
    def classify(data: dict) -> str:
        """Heuristic category guess from the JSON shape rather than the
        folder name, since the exact aircraft/ship subfolder names weren't
        confirmed (see module docstring)."""
        if "DamageParts" in data and "maxFwdSpeed" in data:
            # Ground vehicle or ship both have maxFwdSpeed + DamageParts.hull;
            # ships additionally tend to carry buoyancy/list-recovery keys.
            if any(k in data for k in ("metacentricHeight", "buoyancy", "floatability")):
                return "fleet"
            return "army"
        if any(k in data for k in ("wingArea", "flightModel", "aerodynamics", "maxEngineTemp")):
            return "aviation" if "rotor" not in json.dumps(data)[:2000].lower() else "helicopters"
        return "unknown"

    def _extract_crew_count(self, damage_parts: dict) -> Optional[int]:
        """NOT a naive count of DamageParts.crew keys. The real Leopard 2A5
        record lists 4 loader_*_dm and 12 machine_gunner_*_dm entries even
        though the vehicle has 4 real crew — those extra keys are hit-
        detection zones (multiple hitboxes per crewman / turret position),
        not distinct people. Counting them directly overstates crew by 3-4x.
        Until this is cross-referenced against the wiki's stated crew count
        (WikiExtractor's infobox pull has this as a plain "Crew" field),
        return None rather than a confidently wrong number."""
        return None

    # DamageParts groups whose name suggests they hold real protective
    # value. CONFIRMED against the real germ_leopard_2a5.blkx record: a
    # naive scan of just "hull"/"turret" catches only thin structural
    # backing plates (13-45mm there). The actual composite/NERA protection
    # (400-650mm effective, same record) lives in separately-named groups —
    # that file has hull_front_composite_armor, turret_composite_armor,
    # turret_ex_special_armor, heavy_turret_screens, and heavy_body_screens
    # alongside plain hull/turret. Group naming isn't fully standardized
    # across vehicles (this is a genuinely hard problem — it's why
    # dedicated "armor viewer" tools exist as their own projects in this
    # community), so this matches on substring hints and explicitly
    # excludes groups that carry an armorThickness field for hit-detection
    # purposes but aren't facing protection (optics reticles, wheel/track
    # hitboxes, the in-game x-ray visualization layer).
    ARMOR_GROUP_INCLUDE_HINTS = ("hull", "turret", "composite", "screen", "special_armor", "mask")
    ARMOR_GROUP_EXCLUDE_HINTS = ("xray", "optic", "chassis", "liner", "shield")

    def _armor_bearing_groups(self, damage_parts: dict) -> dict[str, dict]:
        return {
            name: group
            for name, group in damage_parts.items()
            if isinstance(group, dict)
            and any(h in name for h in self.ARMOR_GROUP_INCLUDE_HINTS)
            and not any(h in name for h in self.ARMOR_GROUP_EXCLUDE_HINTS)
        }

    def _extract_armor_facing(self, zone_groups: list[dict], facing_keywords: tuple[str, ...]) -> Optional[int]:
        """Each group holds dozens of individually named damage-model zones
        (e.g. turret_04_front_dm, ex_armor_r_03_dm), not one value per
        facing. Takes the MAX armorThickness across every zone in every
        given group whose name matches the requested facing keyword — the
        strongest point in that facing, not the shape of the weak spots
        around it. Good enough for a sortable "front/side/rear mm" summary
        stat; not a substitute for the real multi-zone model if you're
        building an actual armor viewer."""
        best = None
        for group in zone_groups:
            for zone_name, zone in group.items():
                if not isinstance(zone, dict):
                    continue
                if any(kw in zone_name for kw in facing_keywords):
                    thickness = zone.get("armorThickness")
                    if isinstance(thickness, (int, float)):
                        best = thickness if best is None else max(best, thickness)
        return int(best) if best is not None else None

    def parse_ground_vehicle(self, data: dict, filename: str) -> dict:
        dp = data.get("DamageParts", {})
        armor_groups = self._armor_bearing_groups(dp)
        hull_groups = [g for name, g in armor_groups.items() if "turret" not in name]
        turret_groups = [g for name, g in armor_groups.items() if "turret" in name]
        max_ang_speed = data.get("maxAngSpeed")

        record = {
            "id_hint": Path(filename).stem,  # e.g. "germ_leopard_2a5"
            "source": "datamine",
            "mobility": {
                "weightTons": round(data["mass"] / 1000, 1) if "mass" in data else None,
                # NOTE: blk-derived configs can carry more than one
                # maxFwdSpeed key across different scoped sections (e.g. an
                # arcade-physics override). data.get() below returns
                # whichever value survived JSON parsing — confirm this is
                # the "realistic" figure you want before trusting it in
                # bulk, ideally by spot-checking a few files against the
                # wiki's stated top speed.
                "topSpeedKmh": data.get("maxFwdSpeed"),
                "reverseSpeedKmh": data.get("maxRevSpeed"),
                "turnTimeSec": round(360 / max_ang_speed, 1) if max_ang_speed else None,
            },
            "armor": {
                "hullFrontMm": self._extract_armor_facing(hull_groups, ("front",)),
                "hullSideMm": self._extract_armor_facing(hull_groups, ("side",)),
                "hullRearMm": self._extract_armor_facing(hull_groups, ("back", "rear")),
                "turretFrontMm": self._extract_armor_facing(turret_groups, ("front",)),
                "turretSideMm": self._extract_armor_facing(turret_groups, ("side",)),
                "turretRearMm": self._extract_armor_facing(turret_groups, ("back", "rear")),
            },
            "crew_hint": self._extract_crew_count(dp.get("crew", {})),  # see method docstring — cross-ref with wiki
        }
        return record

    def parse_aircraft_or_helicopter(self, data: dict, filename: str) -> dict:
        """NEEDS VERIFICATION — written from the repo's evident folder
        convention, not a confirmed sample aircraft .blkx (see module
        docstring). Field names below are best-guess based on common
        Dagor-engine naming conventions used elsewhere in this same repo
        (e.g. camelCase, *Kmh / *Ms suffixes) and WILL need correcting
        against a real file before this is trusted. Fetch one, e.g.:
            aces.vromfs.bin_u/gamedata/units/flightmodels/<file>.blkx
        (or whatever the real subfolder turns out to be) and compare keys."""
        record = {
            "id_hint": Path(filename).stem,
            "source": "datamine",
            "_verified": False,
            "mobility": {
                "topSpeedKmh": data.get("maxSpeed") or data.get("VmaxKmh"),
                "climbRateMs": data.get("climbRate") or data.get("maxClimbRateMs"),
            },
        }
        return record

    def extract_all(self) -> list[dict]:
        records = []
        files = list(self.iter_unit_files())
        log.info("Found %d unit files under %s", len(files), self.UNITS_SUBPATH)
        for path in files:
            try:
                data = json.loads(path.read_text())
            except json.JSONDecodeError:
                log.warning("Skipping unparseable file: %s", path)
                continue

            category = self.classify(data)
            if category == "army":
                records.append(self.parse_ground_vehicle(data, path.name))
            elif category in ("aviation", "helicopters"):
                rec = self.parse_aircraft_or_helicopter(data, path.name)
                records.append(rec)
            elif category == "fleet":
                # Ships share the ground-vehicle DamageParts shape closely
                # enough that the same parser's armor/mobility extraction
                # is a reasonable starting point; hull-form-specific fields
                # (draft, displacement) aren't handled yet.
                records.append(self.parse_ground_vehicle(data, path.name))
            else:
                log.debug("Unclassified unit file, skipping: %s", path)
        return records


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------

def merge_sources(wiki_records: list[dict], datamine_records: list[dict]) -> list[dict]:
    """Join on a loose slug match between the wiki page title and the
    datamine id_hint. Real-world titles and internal model slugs diverge
    enough (spacing, punctuation, "Leopard 2A5" vs "leopard_2a5") that a
    production version of this should use a maintained name-mapping table
    rather than pure fuzzy matching — sketching the shape of that join here
    rather than shipping a fragile matcher that looks more solid than it is.
    """
    def slugify(s: str) -> str:
        return "".join(c.lower() if c.isalnum() else "_" for c in s).strip("_")

    datamine_by_slug = {slugify(r["id_hint"]): r for r in datamine_records}

    merged = []
    for w in wiki_records:
        slug = slugify(w["name"])
        dm = datamine_by_slug.get(slug)
        entry = {**w}
        if dm:
            entry["mobility"] = dm.get("mobility")
            entry["armor"] = dm.get("armor")
            entry["_matched_datamine_file"] = dm["id_hint"]
        else:
            entry["_matched_datamine_file"] = None
        merged.append(entry)
    return merged


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_wiki = sub.add_parser("wiki", help="Scrape the Fandom wiki for one nation/category")
    p_wiki.add_argument("--nation", required=True, choices=sorted(NATION_TO_WIKI_CATEGORY))
    p_wiki.add_argument("--category", required=True, choices=sorted(CATEGORY_TO_WIKI_SUFFIX))
    p_wiki.add_argument("--limit", type=int, default=200)
    p_wiki.add_argument("--out", required=True, type=Path)

    p_dm = sub.add_parser("datamine", help="Parse a local (or freshly cloned) datamine checkout")
    p_dm.add_argument("--repo-path", required=True, type=Path)
    p_dm.add_argument("--no-clone", action="store_true", help="Fail instead of cloning if repo-path is missing")
    p_dm.add_argument("--out", required=True, type=Path)

    p_merge = sub.add_parser("merge", help="Join wiki + datamine output into the Vehicle shape")
    p_merge.add_argument("--wiki", required=True, type=Path)
    p_merge.add_argument("--datamine", required=True, type=Path)
    p_merge.add_argument("--out", required=True, type=Path)

    args = parser.parse_args()

    if args.command == "wiki":
        records = WikiExtractor().extract_nation_category(args.nation, args.category, limit=args.limit)
        args.out.write_text(json.dumps(records, indent=2))
        log.info("Wrote %d wiki records → %s", len(records), args.out)

    elif args.command == "datamine":
        extractor = DatamineExtractor.ensure_repo(args.repo_path, clone_if_missing=not args.no_clone)
        records = extractor.extract_all()
        args.out.write_text(json.dumps(records, indent=2))
        log.info("Wrote %d datamine records → %s", len(records), args.out)

    elif args.command == "merge":
        wiki_records = json.loads(args.wiki.read_text())
        datamine_records = json.loads(args.datamine.read_text())
        merged = merge_sources(wiki_records, datamine_records)
        args.out.write_text(json.dumps(merged, indent=2))
        log.info("Wrote %d merged records → %s", len(merged), args.out)


if __name__ == "__main__":
    main()
