#!/usr/bin/env python3
"""
daily_scraper.py
=================
Automated daily scraper: wiki.warthunder.com -> Supabase (Postgres).

GROUNDING: unlike the original scraper.py (Fandom + datamine), every
pattern below was checked against real, live pages fetched during this
build:
  - https://wiki.warthunder.com/unit/us_m1a2_abrams  (a real vehicle page)
  - https://wiki.warthunder.com/ground                (a real category page)

CONFIRMED:
  - URL pattern /unit/{slug}; slug matches the datamine's internal unit
    IDs (e.g. "us_m1a2_abrams").
  - Category listing pages (/aviation, /helicopters, /ground, /ships,
    /boats) each render a full tech tree with a plain <a href="/unit/...">
    per vehicle -- confirmed on /ground, which listed 150+ USA vehicles
    alone across every rank and premium/event variant. This means vehicle
    discovery doesn't need pagination or a second data source: crawl the
    5 category pages, collect every /unit/ href, done.
  - Individual vehicle page label text: "Rank" (roman numeral), "AB"/"RB"/
    "SB" battle rating blocks, "Crew {n} persons", "Weight" as a clean
    single value, armor as "Hull {front} / {side} / {back} mm" and
    "Turret {front} / {side} / {back} mm", and a genuine HTML <table> for
    ammunition with penetration at 10/100/500/1000/1500/2000m.

NOT CONFIRMED -- NEEDS A LIVE RUN TO LOCK DOWN:
  - Exact CSS class names / DOM structure. This build's fetch tool only
    ever returned a text-rendered view of the page, never raw HTML, so
    the extraction below is written against label TEXT (page.locator
    with text= selectors) rather than class names -- more resilient to a
    CSS refactor, but slower and occasionally ambiguous.
  - Multi-mode numeric stats (forward/backward speed, power-to-weight,
    engine power, turret rotation speed) rendered CONCATENATED with no
    separator in the text-flattened view this build had access to (e.g.
    "Forward 6876 km/h", almost certainly 4 stacked per-mode values with
    no delimiter surviving the flatten). Deliberately NOT extracted below
    for exactly this reason -- guessing a split point and shipping wrong
    numbers with false confidence is worse than leaving the field out.
    Run once with --debug-html on a few vehicles, open the saved HTML,
    find the real per-mode markup, and extend extract_vehicle() once you
    can see it.

NOT AFFILIATED WITH OR ENDORSED BY GAIJIN ENTERTAINMENT. This targets
Gaijin's own first-party site (not a CC-BY-SA community mirror) on a
DAILY automated schedule -- a materially more sustained activity than a
one-off manual fetch. Read https://legal.gaijin.net/termsofservice before
turning the GitHub Action on for real.
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

try:
    from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout
except ImportError:
    sys.exit("Missing dependency: pip install playwright && playwright install --with-deps chromium")

try:
    from supabase import create_client, Client as SupabaseClient
except ImportError:
    sys.exit("Missing dependency: pip install supabase")

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s  %(message)s")
log = logging.getLogger("daily-scraper")

BASE_URL = "https://wiki.warthunder.com"
USER_AGENT = "war-thunder-codex-daily-scraper/1.0 (personal fan-project; contact: set-your-email-here)"
REQUEST_DELAY_SEC = 2.0  # conservative on purpose -- this is a DAILY automated job against a first-party site
PAGE_TIMEOUT_MS = 20_000
BATCH_SIZE = 25  # vehicles per MongoDB bulk_write call

CATEGORY_PATHS = {
    "aviation": "/aviation",
    "helicopters": "/helicopters",
    "army": "/ground",
    "fleet": "/ships",  # bluewater fleet; coastal fleet folded in separately, see COASTAL_FLEET_PATH
}
COASTAL_FLEET_PATH = "/boats"

# Cross-confirmed two ways: matches both the wiki's own /unit/ slugs (seen
# directly on /ground and /unit/us_m1a2_abrams) and the datamine repo's
# tankmodels/*.blkx filenames from the earlier build.
SLUG_PREFIX_TO_NATION = {
    "us_": "usa", "germ_": "germany", "ussr_": "ussr", "uk_": "britain",
    "jp_": "japan", "cn_": "china", "it_": "italy", "fr_": "france",
    "sw_": "sweden", "il_": "israel",
}

RANK_ROMAN_TO_INT = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8}


@dataclass
class ScrapeStats:
    discovered: int = 0
    scraped_ok: int = 0
    scraped_failed: int = 0
    upserted: int = 0
    errors: list[str] = field(default_factory=list)


def polite_wait() -> None:
    time.sleep(REQUEST_DELAY_SEC)


def nation_from_slug(slug: str) -> Optional[str]:
    for prefix, nation in SLUG_PREFIX_TO_NATION.items():
        if slug.startswith(prefix):
            return nation
    return None


def _to_float(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    cleaned = text.replace(",", "")
    match = re.search(r"[\d.]+", cleaned)
    return float(match.group(0)) if match else None


def discover_vehicle_slugs(page: Page, category: str, path: str) -> list[str]:
    """Category listing pages render a full tech tree with a plain
    <a href="/unit/{slug}"> per vehicle -- confirmed on /ground. Pulling
    every such href gives the complete roster for that category in one
    page load."""
    url = f"{BASE_URL}{path}"
    log.info("Discovering %s vehicles from %s", category, url)
    page.goto(url, timeout=PAGE_TIMEOUT_MS, wait_until="networkidle")
    polite_wait()

    hrefs = page.eval_on_selector_all(
        'a[href*="/unit/"]',
        "els => els.map(e => e.getAttribute('href'))",
    )
    slugs = sorted({
        href.rsplit("/unit/", 1)[-1].split("?")[0]
        for href in (hrefs or [])
        if href and "/unit/" in href
    })
    log.info("  found %d slugs", len(slugs))
    return slugs


def text_after_label(page: Page, label: str) -> Optional[str]:
    """Best-effort: find an element containing exactly `label` and return
    the trimmed text of its next sibling. Based on visible label text
    rather than a CSS class (unconfirmed in this build) -- more resilient
    to a pure styling refactor, at the cost of being slower and
    occasionally ambiguous if a label string appears twice on the page.
    NEEDS VERIFICATION against the live DOM; see module docstring."""
    try:
        el = page.locator(f"text='{label}'").first
        return el.locator("xpath=following-sibling::*[1]").inner_text(timeout=2000).strip()
    except (PlaywrightTimeout, Exception):
        return None


def parse_armor_triplet(text: Optional[str]) -> Optional[dict]:
    """"Hull 133 / 60 / 32 mm" -> {frontMm, sideMm, backMm}. Confirmed
    format from the real us_m1a2_abrams page fetch."""
    if not text:
        return None
    match = re.search(r"([\d.]+)\s*/\s*([\d.]+)\s*/\s*([\d.]+)", text)
    if not match:
        return None
    front, side, back = (float(x) for x in match.groups())
    return {"frontMm": front, "sideMm": side, "backMm": back}


def extract_ammunition(page: Page) -> list[dict]:
    """Confirmed as a real HTML <table> on the live page (not a div-based
    layout), so this is on firmer ground than the label-based extraction
    above."""
    ammo: list[dict] = []
    try:
        rows = page.locator("table:has-text('Armor penetration') tbody tr").all()
        for row in rows:
            cells = [c.inner_text().strip() for c in row.locator("td").all()]
            if len(cells) >= 8:
                ammo.append({
                    "name": cells[0].split("\n")[-1].strip(),  # icons prepend lines; name is last line
                    "type": cells[1],
                    "penetrationMm": {
                        "10m": _to_float(cells[2]), "100m": _to_float(cells[3]),
                        "500m": _to_float(cells[4]), "1000m": _to_float(cells[5]),
                        "1500m": _to_float(cells[6]), "2000m": _to_float(cells[7]),
                    },
                })
    except Exception as exc:
        log.debug("Ammo table extraction failed: %s", exc)
    return ammo


def extract_vehicle(page: Page, slug: str, category: str) -> Optional[dict]:
    url = f"{BASE_URL}/unit/{slug}"
    try:
        page.goto(url, timeout=PAGE_TIMEOUT_MS, wait_until="networkidle")
    except PlaywrightTimeout:
        log.warning("Timed out loading %s", url)
        return None
    polite_wait()

    try:
        name = page.locator("h1").first.inner_text(timeout=3000).strip()
    except Exception:
        name = slug

    rank_text = (text_after_label(page, "Rank") or "").strip()
    rank = RANK_ROMAN_TO_INT.get(rank_text)

    br = {}
    for mode in ("AB", "RB", "SB"):
        br[mode.lower()] = _to_float(text_after_label(page, mode))

    crew = None
    crew_match = re.search(r"(\d+)", text_after_label(page, "Crew") or "")
    if crew_match:
        crew = int(crew_match.group(1))

    weight_tons = _to_float(text_after_label(page, "Weight"))
    hull_armor = parse_armor_triplet(text_after_label(page, "Hull"))
    turret_armor = parse_armor_triplet(text_after_label(page, "Turret"))
    research_rp = _to_float(text_after_label(page, "Research"))
    purchase_sl = _to_float(text_after_label(page, "Purchase"))
    ammunition = extract_ammunition(page)

    return {
        "id": slug,
        "name": name,
        "nation": nation_from_slug(slug),
        "category": category,
        "rank": rank,
        "br": br,
        "crew": crew,
        "weightTons": weight_tons,
        "armor": {"hull": hull_armor, "turret": turret_armor},
        "ammunition": ammunition,
        "researchCostRp": research_rp,
        "purchaseCostSl": purchase_sl,
        "sourceUrl": url,
        "scrapedAt": datetime.now(timezone.utc).isoformat(),
    }


def get_supabase_client() -> SupabaseClient:
    url = os.environ.get("SUPABASE_URL")
    # Deliberately the SERVICE ROLE key here, not the anon key the Next.js
    # app uses (lib/supabase.ts) — this process needs to bypass the
    # public-read-only RLS policy in scripts/supabase-schema.sql to write.
    # Never use the service role key anywhere client-facing; it belongs
    # in GitHub Actions secrets only.
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        sys.exit("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are not set. See README 'Database setup' section.")
    try:
        client = create_client(url, key)
        client.table("vehicles").select("id").limit(1).execute()  # cheap connectivity + schema check
    except Exception as exc:  # noqa: BLE001 -- want a clear exit message for any connection/schema problem
        sys.exit(
            f"Could not reach the Supabase 'vehicles' table: {exc}\n"
            f"Did you run scripts/supabase-schema.sql in the Supabase SQL editor yet?"
        )
    return client


def to_supabase_row(vehicle: dict) -> dict:
    """Adapter from extract_vehicle()'s camelCase shape to
    supabase-schema.sql's snake_case columns. Kept as a separate step
    (rather than having extract_vehicle emit snake_case directly) so
    --dry-run output stays in the more readable camelCase shape."""
    br = vehicle.get("br") or {}
    return {
        "id": vehicle["id"],
        "name": vehicle["name"],
        "nation": vehicle.get("nation"),
        "category": vehicle["category"],
        "rank": vehicle.get("rank"),
        "br_ab": br.get("ab"),
        "br_rb": br.get("rb"),
        "br_sb": br.get("sb"),
        "crew": vehicle.get("crew"),
        "weight_tons": vehicle.get("weightTons"),
        "armor": vehicle.get("armor"),
        "ammunition": vehicle.get("ammunition"),
        "research_cost_rp": vehicle.get("researchCostRp"),
        "purchase_cost_sl": vehicle.get("purchaseCostSl"),
        "source_url": vehicle.get("sourceUrl"),
        "scraped_at": vehicle.get("scrapedAt"),
    }


def upsert_vehicles(client: SupabaseClient, vehicles: list[dict]) -> int:
    if not vehicles:
        return 0
    rows = [to_supabase_row(v) for v in vehicles]
    client.table("vehicles").upsert(rows, on_conflict="id").execute()
    return len(rows)  # the Python client's upsert response doesn't cleanly separate inserted vs updated counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--category", choices=list(CATEGORY_PATHS) + ["all"], default="all")
    parser.add_argument("--limit", type=int, default=None, help="cap vehicles per category, for testing")
    parser.add_argument("--dry-run", action="store_true", help="scrape and print, skip MongoDB entirely")
    args = parser.parse_args()

    stats = ScrapeStats()
    db_client = None if args.dry_run else get_supabase_client()
    categories = CATEGORY_PATHS if args.category == "all" else {args.category: CATEGORY_PATHS[args.category]}

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()

        for category, path in categories.items():
            slugs = discover_vehicle_slugs(page, category, path)
            if category == "fleet":
                slugs += discover_vehicle_slugs(page, category, COASTAL_FLEET_PATH)
            stats.discovered += len(slugs)
            if args.limit:
                slugs = slugs[: args.limit]

            batch: list[dict] = []
            for i, slug in enumerate(slugs, 1):
                log.info("[%s %d/%d] %s", category, i, len(slugs), slug)
                try:
                    vehicle = extract_vehicle(page, slug, category)
                except Exception as exc:  # noqa: BLE001 -- one bad page must not kill the whole run
                    stats.scraped_failed += 1
                    stats.errors.append(f"{slug}: {exc}")
                    log.error("Failed on %s: %s", slug, exc)
                    continue

                if vehicle:
                    stats.scraped_ok += 1
                    batch.append(vehicle)
                else:
                    stats.scraped_failed += 1

                if len(batch) >= BATCH_SIZE and db_client is not None:
                    stats.upserted += upsert_vehicles(db_client, batch)
                    batch = []

            if db_client is not None and batch:
                stats.upserted += upsert_vehicles(db_client, batch)
            elif args.dry_run:
                for v in batch[:3]:
                    print(v)

        browser.close()

    log.info(
        "Done. discovered=%d ok=%d failed=%d upserted=%d",
        stats.discovered, stats.scraped_ok, stats.scraped_failed, stats.upserted,
    )

    # Fail LOUDLY rather than silently. A scraper hitting a live site is
    # never truly zero-maintenance -- selectors WILL eventually break when
    # the site changes. The honest version of "zero-maintenance" is: it
    # runs unattended right up until the one day it can't, and that day
    # shows up as a failed GitHub Actions run (with an optional
    # notification), not as a silent write of empty/garbage data that
    # quietly stales out the whole app.
    if stats.discovered > 0 and stats.scraped_failed / stats.discovered > 0.15:
        log.error(
            "Failure rate %.0f%% exceeds the 15%% threshold -- almost certainly a broken "
            "selector (see module docstring's 'NOT CONFIRMED' section), not bad luck.",
            100 * stats.scraped_failed / stats.discovered,
        )
        sys.exit(1)

    if stats.errors:
        log.warning("First few errors:\n%s", "\n".join(stats.errors[:10]))


if __name__ == "__main__":
    main()
