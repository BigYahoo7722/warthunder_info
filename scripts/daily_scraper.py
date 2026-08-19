#!/usr/bin/env python3
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
    sys.exit("Missing dependency: pip install playwright supabase")

try:
    from supabase import create_client, Client as SupabaseClient
except ImportError:
    sys.exit("Missing dependency: pip install supabase")

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s  %(message)s")
log = logging.getLogger("wt-codex-scraper")

BASE_URL = "https://wiki.warthunder.com"
USER_AGENT = "war-thunder-codex-bot/3.2"
REQUEST_DELAY_SEC = 1.5
PAGE_TIMEOUT_MS = 30_000
BATCH_SIZE = 20
NAV_RETRIES = 2  # extra attempts if a page load times out / errors
# If more than this fraction of discovered vehicles fail to scrape or save,
# the run exits non-zero so the GitHub Actions run shows red instead of
# quietly finishing "green" with a half-empty (or empty) roster.
MAX_FAILURE_RATIO = 0.15

CATEGORY_PATHS = {
    "aviation": "/aviation",
    "helicopters": "/helicopters",
    "army": "/ground",
    "fleet": "/ships",
}
COASTAL_FLEET_PATH = "/boats"

# FIX: values are now lowercase to match lib/taxonomy.ts's Nation ids
# ("usa", "germany", "ussr", ...). The scraper used to write Title-Case
# names ("USA", "Germany", ...) which never matched the frontend's
# case-sensitive Postgres filter (`.eq("nation", nation)`), so every
# nation/category query on the live site silently returned zero rows even
# though the scraper had successfully written data.
SLUG_PREFIX_TO_NATION = {
    "us_": "usa", "germ_": "germany", "ussr_": "ussr", "su_": "ussr",
    "uk_": "britain", "gb_": "britain", "jp_": "japan", "cn_": "china",
    "it_": "italy", "fr_": "france", "sw_": "sweden", "il_": "israel",
    "za_": "south_africa", "fi_": "finland", "hu_": "hungary",
}

RANK_ROMAN_TO_INT = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8}
# Matches a standalone roman numeral I-VIII inside noisier strings like
# "Rank IV" or "IV " (previous version only did an exact dict lookup on the
# raw scraped text, which broke the moment the label had any extra
# whitespace or a leading "Rank" prefix).
_RANK_RE = re.compile(r"\b(VIII|VII|VI|V|IV|III|II|I)\b")


@dataclass
class ScrapeStats:
    discovered: int = 0
    upserted: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)


# ---------- optional day-of-week auto schedule ----------
# Not used by the GitHub Actions workflows (each one always passes an
# explicit --category); kept only for local/manual runs that want
# auto-rotation. Matches the real weekly schedule 1:1 so it can never
# silently drift out of sync with .github/workflows/scraper-*.yml again:
#   Saturday  -> aviation
#   Sunday    -> army (ground)
#   Monday    -> helicopters
#   Tuesday   -> fleet
#   Wed-Fri   -> rest days, nothing scheduled
def get_category_for_today() -> Optional[str]:
    day = datetime.now(timezone.utc).weekday()  # Python: 0=Mon ... 6=Sun
    if day == 5:
        return "aviation"
    if day == 6:
        return "army"
    if day == 0:
        return "helicopters"
    if day == 1:
        return "fleet"
    return None
# ------------------------------------------------------------------------


def get_nation_smart(slug: str, dynamic_data: dict, flag_country: Optional[str] = None) -> str:
    """FIX: previously only checked SLUG_PREFIX_TO_NATION, which happens to
    cover ground-vehicle slugs (they're prefixed, e.g. "us_m1a2_abrams")
    but NOT aircraft/helicopter slugs (they never carry a country prefix —
    e.g. "p-51d-5", "p-51d-20-na"). Every aviation/helicopter row was
    silently landing on the "unknown" fallback as a result — confirmed
    against the live Supabase table (1,279 aviation rows with
    nation='unknown', 0 with a real nation). The country flag icon
    (<img src=".../country_svg/country_usa.svg">) is present on every
    vehicle page regardless of category, so it's used as the primary
    signal now; the slug-prefix table is kept only as a secondary check
    for the (rare) case the flag icon fails to load/parse."""
    if flag_country:
        return flag_country

    for prefix, nation in SLUG_PREFIX_TO_NATION.items():
        if slug.lower().startswith(prefix):
            return nation

    if "country" in dynamic_data and dynamic_data["country"]:
        return dynamic_data["country"].strip().lower().replace(" ", "_")

    return "unknown"


def _to_float(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    match = re.search(r"[\d.]+", text.replace(",", ""))
    return float(match.group(0)) if match else None


def _extract_rank(dynamic_data: dict) -> Optional[int]:
    """FIX: the old version did RANK_ROMAN_TO_INT.get(dynamic_data.get('rank', 'I'))
    — an exact-match dict lookup against raw scraped text. Any extra
    whitespace, a "Rank" prefix, or the key being named something other
    than exactly 'rank' (e.g. from a locale variant) silently produced
    None instead of the real rank. This scans every dynamic_data value for
    a roman-numeral token."""
    raw = dynamic_data.get("rank")
    if raw:
        m = _RANK_RE.search(raw.upper())
        if m:
            return RANK_ROMAN_TO_INT.get(m.group(1))
    # fallback: some pages don't label the row exactly "rank"
    for v in dynamic_data.values():
        if isinstance(v, str):
            m = _RANK_RE.fullmatch(v.strip().upper())
            if m:
                return RANK_ROMAN_TO_INT.get(m.group(1))
    return None


def extract_vehicle_smart(page: Page, slug: str, category: str) -> Optional[dict]:
    url = f"{BASE_URL}/unit/{slug}"

    last_err: Optional[Exception] = None
    for attempt in range(1, NAV_RETRIES + 2):
        try:
            page.goto(url, timeout=PAGE_TIMEOUT_MS, wait_until="domcontentloaded")
            last_err = None
            break
        except Exception as e:
            last_err = e
            log.warning(f"[{slug}] load attempt {attempt} failed: {e}")
            time.sleep(REQUEST_DELAY_SEC)
    if last_err is not None:
        log.error(f"[{slug}] giving up after {NAV_RETRIES + 1} attempts: {last_err}")
        return None

    time.sleep(REQUEST_DELAY_SEC)

    try:
        page_data = page.evaluate(r"""() => {
            let dynamicData = {};
            document.querySelectorAll('.infobox tr, .specs-card tr').forEach(row => {
                let th = row.querySelector('th');
                let td = row.querySelector('td');
                if (th && td) {
                    let key = th.innerText.trim().replace(/[^a-zA-Z0-9 ]/g, "").replace(/\s+/g, "_").toLowerCase();
                    dynamicData[key] = td.innerText.trim();
                }
            });

            let ogImage = document.querySelector('meta[property="og:image"]');
            let imgUrl = ogImage ? ogImage.content : null;

            if (!imgUrl) {
                let fallbackImg = document.querySelector('.image img');
                imgUrl = fallbackImg ? fallbackImg.src : null;
            }

            // FIX: the country flag icon is present on every vehicle page
            // regardless of category (aviation/army/fleet/helicopters) and
            // encodes the nation directly in its filename, e.g.
            // ".../country_svg/country_usa.svg" -> "usa". This is far more
            // reliable than guessing from the URL slug, which only ever
            // works for ground vehicles.
            let flagCountry = null;
            let flagImg = document.querySelector('img[src*="/country_svg/country_"]');
            if (flagImg && flagImg.src) {
                let m = flagImg.src.match(/country_svg\/country_([a-z_]+?)(?:_modern|_early|_h\d*)?\.svg/i);
                if (m) flagCountry = m[1].toLowerCase();
            }

            // ---- deep spec extraction (label-based, not CSS-class-based) ----
            // Calibrated against a real fetched wiki.warthunder.com page
            // (M1A2 Abrams), since the actual DOM structure here is NOT a
            // classic <th>/<td> wiki table (the old ".infobox tr" selector
            // above matches nothing) — it's a card layout where the VALUE
            // renders before its label, e.g. "VII Rank", "AB 12.0 RB 12.0
            // SB 12.0 Battle rating". Collapsing all whitespace to single
            // spaces makes these reliably matchable with regex.
            const flat = document.body.innerText.replace(/\s+/g, ' ').trim();
            function grab(re) { const m = flat.match(re); return m; }

            const rankM = grab(/\b([IVX]{1,4})\s+Rank\b/);
            const brM = grab(/AB\s+([\d.]+)\s+RB\s+([\d.]+)\s+SB\s+([\d.]+)\s+Battle rating/);
            const costM = grab(/Main role\s+([\d,]+)\s+Research\s+([\d,]+)\s+Purchase/);
            const crewM = grab(/Crew\s+(\d+)\s*persons?/i);
            const visM = grab(/Visibility\s+(\d+)\s*%/);
            const hullM = grab(/Hull\s+([\d.]+)\s*\/\s*([\d.]+)\s*\/\s*([\d.]+)\s*mm/);
            const turretM = grab(/Turret\s+([\d.]+)\s*\/\s*([\d.]+)\s*\/\s*([\d.]+)\s*mm/);
            const weightM = grab(/Weight\s+([\d.]+)\s*t\b/);
            const reloadM = grab(/Reload basic crew.*?aces\s+([\d.]+)\s*(?:\u2192|->)\s*([\d.]+)\s*s/);
            const compositeArmor = /Composite armour/i.test(flat);
            const eraArmor = /Explosive reactive armour|\bERA\b/i.test(flat);

            // Ammunition table: real <table> elements exist for weapons,
            // so this part is high-confidence (not text-flattened guessing).
            const ammo = [];
            document.querySelectorAll('table').forEach(table => {
                const rows = Array.from(table.querySelectorAll('tr')).slice(1);
                rows.forEach(row => {
                    const cells = Array.from(row.querySelectorAll('td')).map(c => c.innerText.trim());
                    if (cells.length >= 8) {
                        const rawName = cells[0].replace(/^[^A-Za-z0-9]*/, '').trim();
                        const type = cells[1];
                        const ranges = ['10m', '100m', '500m', '1000m', '1500m', '2000m'];
                        const pen = {};
                        ranges.forEach((r, i) => {
                            const v = parseFloat(cells[2 + i]);
                            pen[r] = isNaN(v) ? null : v;
                        });
                        if (rawName && type) ammo.push({ name: rawName, type: type, penetrationMm: pen });
                    }
                });
            });

            return {
                title: document.title,
                h1: document.querySelector('h1') ? document.querySelector('h1').innerText : '',
                imageUrl: imgUrl,
                dynamicData: dynamicData,
                flagCountry: flagCountry,
                rankRoman: rankM ? rankM[1] : null,
                brAb: brM ? brM[1] : null,
                brRb: brM ? brM[2] : null,
                brSb: brM ? brM[3] : null,
                researchCostRp: costM ? costM[1] : null,
                purchaseCostSl: costM ? costM[2] : null,
                crew: crewM ? crewM[1] : null,
                visibilityPct: visM ? visM[1] : null,
                hullArmor: hullM ? [hullM[1], hullM[2], hullM[3]] : null,
                turretArmor: turretM ? [turretM[1], turretM[2], turretM[3]] : null,
                composite: compositeArmor,
                era: eraArmor,
                weightTons: weightM ? weightM[1] : null,
                reloadBasicSec: reloadM ? reloadM[1] : null,
                reloadAcedSec: reloadM ? reloadM[2] : null,
                ammo: ammo
            };
        }""")
    except Exception as e:
        log.error(f"JS extraction failed on {slug}: {e}")
        page_data = {"h1": "", "title": "", "imageUrl": None, "dynamicData": {}, "flagCountry": None}

    name = re.sub(r'[\-\|]?\s*War Thunder.*$', '', page_data['h1'] or page_data['title']).strip()
    if not name:
        name = slug.replace("_", " ").title()

    nation = get_nation_smart(slug, page_data.get("dynamicData", {}), page_data.get("flagCountry"))

    img_url = page_data.get("imageUrl")
    if img_url and str(img_url).startswith('/'):
        img_url = f"{BASE_URL}{img_url}"

    # Prefer the page's own "VII Rank" style value; fall back to the old
    # generic-table-based guess (rarely fires now, kept as a safety net).
    rank_val = RANK_ROMAN_TO_INT.get((page_data.get("rankRoman") or "").upper()) \
        or _extract_rank(page_data.get("dynamicData", {}))

    def _num(v):
        if v in (None, ""):
            return None
        try:
            return float(str(v).replace(",", ""))
        except ValueError:
            return None

    hull = page_data.get("hullArmor")
    turret = page_data.get("turretArmor")
    armor = None
    if hull or turret:
        armor = {
            "hull": {"frontMm": _num(hull[0]), "sideMm": _num(hull[1]), "backMm": _num(hull[2])} if hull else None,
            "turret": {"frontMm": _num(turret[0]), "sideMm": _num(turret[1]), "backMm": _num(turret[2])} if turret else None,
            "composite": bool(page_data.get("composite")),
            "era": bool(page_data.get("era")),
        }

    ammo_raw = page_data.get("ammo") or []
    ammunition = [{"name": a["name"], "type": a["type"], "penetrationMm": a["penetrationMm"]} for a in ammo_raw] or None

    return {
        "id": slug,
        "name": name,
        "nation": nation,
        "category": category,
        "rank": rank_val,
        "brAb": _num(page_data.get("brAb")),
        "brRb": _num(page_data.get("brRb")),
        "brSb": _num(page_data.get("brSb")),
        "crew": int(_num(page_data.get("crew"))) if _num(page_data.get("crew")) is not None else None,
        "weightTons": _num(page_data.get("weightTons")),
        "armor": armor,
        "ammunition": ammunition,
        "researchCostRp": _num(page_data.get("researchCostRp")),
        "purchaseCostSl": _num(page_data.get("purchaseCostSl")),
        "imageUrl": img_url,
        "sourceUrl": url,
        "scrapedAt": datetime.now(timezone.utc).isoformat(),
        "dynamicSpecs": page_data.get("dynamicData", {}),
    }


def get_supabase_client() -> SupabaseClient:
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])


def upsert_vehicles(client: SupabaseClient, vehicles: list[dict], stats: ScrapeStats) -> int:
    """FIX: this used to run with no try/except at all — a single bad batch
    (e.g. a schema mismatch like the missing dynamic_specs column) crashed
    the whole script immediately, before any later batches even had a
    chance to run. Now a failed batch is logged and counted as failed
    instead of taking down the entire scrape."""
    if not vehicles:
        return 0
    rows = []
    for v in vehicles:
        rows.append({
            "id": v["id"],
            "name": v["name"],
            "nation": v["nation"],
            "category": v["category"],
            "rank": v["rank"],
            "br_ab": v.get("brAb"),
            "br_rb": v.get("brRb"),
            "br_sb": v.get("brSb"),
            "crew": v.get("crew"),
            "weight_tons": v.get("weightTons"),
            "armor": v.get("armor"),
            "ammunition": v.get("ammunition"),
            "research_cost_rp": v.get("researchCostRp"),
            "purchase_cost_sl": v.get("purchaseCostSl"),
            "image_url": v.get("imageUrl"),
            "source_url": v["sourceUrl"],
            "scraped_at": v["scrapedAt"],
            "dynamic_specs": v.get("dynamicSpecs", {}),
        })
    try:
        client.table("vehicles").upsert(rows, on_conflict="id").execute()
        return len(rows)
    except Exception as e:
        msg = f"Batch upsert failed ({len(rows)} rows, ids {rows[0]['id']}..{rows[-1]['id']}): {e}"
        log.error(msg)
        stats.errors.append(msg)
        stats.failed += len(rows)
        return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", default="auto", help="Specify category or leave blank for auto-schedule")
    parser.add_argument("--limit", type=int, default=None, help="Only process the first N discovered vehicles (for --dry-run sanity checks)")
    parser.add_argument("--dry-run", action="store_true", help="Scrape and log, but never write to Supabase")
    args = parser.parse_args()

    target_category = args.category
    if target_category == "auto":
        target_category = get_category_for_today()
        if not target_category:
            log.info("Auto-Scheduler: today is a rest day, nothing to do.")
            sys.exit(0)
        log.info(f"Auto-Scheduler: targeting [{target_category.upper()}]")

    client = None if args.dry_run else get_supabase_client()
    stats = ScrapeStats()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()

        paths = [CATEGORY_PATHS[target_category]] if target_category in CATEGORY_PATHS else []
        if target_category == "fleet":
            paths.append(COASTAL_FLEET_PATH)

        slugs = []
        for path in paths:
            page.goto(f"{BASE_URL}{path}", wait_until="domcontentloaded")
            elements = page.eval_on_selector_all('a[href*="/unit/"]', "els => els.map(e => e.getAttribute('href'))")
            slugs.extend([e.rsplit("/unit/", 1)[-1].split("?")[0] for e in elements if "/unit/" in e])

        slugs = sorted(set(slugs))
        if args.limit:
            slugs = slugs[: args.limit]
        stats.discovered = len(slugs)

        if stats.discovered == 0:
            log.error(
                f"Discovered 0 vehicles at {paths} — the category page's markup likely "
                f"changed (selector 'a[href*=\"/unit/\"]' matched nothing). Treating this "
                f"as a hard failure rather than silently 'succeeding' with an empty run."
            )
            browser.close()
            sys.exit(1)

        batch = []
        for i, slug in enumerate(slugs, 1):
            log.info(f"[{target_category} {i}/{len(slugs)}] Processing {slug}...")
            vehicle = extract_vehicle_smart(page, slug, target_category)
            if vehicle:
                batch.append(vehicle)
            else:
                stats.failed += 1

            if len(batch) >= BATCH_SIZE:
                if args.dry_run:
                    log.info(f"[dry-run] would upsert {len(batch)} rows, e.g. {batch[0]}")
                else:
                    stats.upserted += upsert_vehicles(client, batch, stats)
                batch.clear()

        if batch:
            if args.dry_run:
                log.info(f"[dry-run] would upsert {len(batch)} rows, e.g. {batch[0]}")
            else:
                stats.upserted += upsert_vehicles(client, batch, stats)

        browser.close()

    failure_ratio = (stats.failed / stats.discovered) if stats.discovered else 0
    log.info(
        f"Run complete. Category: {target_category} | Discovered: {stats.discovered} | "
        f"Saved: {stats.upserted} | Failed: {stats.failed} ({failure_ratio:.0%})"
    )
    for err in stats.errors:
        log.error(f"  - {err}")

    if not args.dry_run and failure_ratio > MAX_FAILURE_RATIO:
        log.error(
            f"Failure ratio {failure_ratio:.0%} exceeds the {MAX_FAILURE_RATIO:.0%} threshold "
            f"— exiting non-zero so this shows up as a failed GitHub Actions run instead of "
            f"quietly writing a half-empty roster."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
