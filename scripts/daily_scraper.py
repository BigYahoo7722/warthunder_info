#!/usr/bin/env python3
"""
daily_scraper.py
=================
Automated scraper: wiki.warthunder.com -> Supabase (Postgres). Designed to
run ONE category per invocation (see --category) so it can be scheduled
across different days of the week rather than all at once — see
.github/workflows/daily-scraper.yml, which maps weekday -> category.

GROUNDING: every URL pattern and field label below was checked against
real, live pages fetched during this build:
  - https://wiki.warthunder.com/unit/us_m1a2_abrams  (a real vehicle page)
  - https://wiki.warthunder.com/ground                (a real category page)

CONFIRMED:
  - URL pattern /unit/{slug}; slug matches internal unit IDs
    (e.g. "us_m1a2_abrams") and uses short nation prefixes: us_, germ_,
    ussr_, uk_, jp_, cn_, it_, fr_, sw_, il_ — NOT full nation names.
  - Category listing pages are lowercase: /aviation, /helicopters,
    /ground, /ships, /boats (bluewater + coastal fleet respectively) —
    each renders a full tech tree with a plain <a href="/unit/...">
    per vehicle, confirmed on /ground (150+ USA vehicles alone).
  - Field label text: "Rank" (roman numeral), "AB"/"RB"/"SB" battle
    rating blocks (three SEPARATE labeled values, not one combined
    "Battle Rating: X" line), "Crew {n} persons", "Weight" as a clean
    single value, armor as "Hull {f} / {s} / {b} mm" and "Turret {f} /
    {s} / {b} mm", and a genuine HTML <table> for ammunition with
    penetration at 10/100/500/1000/1500/2000m.

NOT CONFIRMED -- NEEDS A LIVE RUN TO LOCK DOWN:
  - Exact CSS class names / DOM structure (this build only ever had a
    text-rendered view of pages, never raw HTML) -- extraction below is
    written against label TEXT rather than class names for that reason.
  - Multi-mode numeric stats (forward/backward speed, power-to-weight,
    engine power, turret rotation) render CONCATENATED with no separator
    in the text-flattened view available here (e.g. "Forward 6876 km/h"
    -- almost certainly 4 stacked per-mode values). Deliberately NOT
    extracted for exactly this reason: guessing a split point and
    shipping wrong numbers with false confidence is worse than leaving
    the field out. Run once with a saved HTML dump on a few vehicles,
    find the real per-mode markup, and extend extract_vehicle() once you
    can see it.

NOT AFFILIATED WITH OR ENDORSED BY GAIJIN ENTERTAINMENT. This targets
Gaijin's own first-party site on an automated schedule -- a materially
more sustained activity than a one-off manual fetch. Read
https://legal.gaijin.net/termsofservice before relying on the schedule.

Usage:
    python3 daily_scraper.py --category army                    # real run, one category
    python3 daily_scraper.py --category army --limit 10 --dry-run  # safe test, no DB writes
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
USER_AGENT = "war-thunder-codex-daily-scraper/1.1 (personal fan-project; contact: set-your-email-here)"
REQUEST_DELAY_SEC = 2.0  # conservative on purpose -- this is an automated job against a first-party site.
# Worth knowing: even the slowest category (army, likely 800-1500+ vehicles across all nations/ranks) at
# ~3.5s/vehicle including this delay finishes in under 1.5 hours -- there's no time-budget reason to speed
# this up under the weekly-per-category schedule, only a risk-of-getting-blocked reason not to.
PAGE_TIMEOUT_MS = 20_000
BATCH_SIZE = 25  # vehicles per Supabase bulk upsert call

# Confirmed lowercase on the live site -- do not capitalize these, and
# note "fleet" needs BOTH listing pages (bluewater + coastal).
CATEGORY_PATHS = {
    "aviation": "/aviation",
    "helicopters": "/helicopters",
    "army": "/ground",
    "fleet": "/ships",  # + COASTAL_FLEET_PATH below
}
COASTAL_FLEET_PATH = "/boats"

# Cross-confirmed two ways: matches both the wiki's own /unit/ slugs and
# the community datamine repo's tankmodels/*.blkx filenames from an
# earlier build. Full nation NAMES ("usa", "germany") do NOT appear in
# slugs -- only these short prefixes do.
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
    <a href="/unit/{slug}"> per vehicle -- confirmed on /ground."""
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
    rather than a CSS class (unconfirmed -- see module docstring)."""
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
    """Confirmed as a real HTML <table> on the live page."""
    ammo: list[dict] = []
    try:
        rows = page.locator("table:has-text('Armor penetration') tbody tr").all()
        for row in rows:
            cells = [c.inner_text().strip() for c in row.locator("td").all()]
            if len(cells) >= 8:
                ammo.append({
                    "name": cells[0].split("\n")[-1].strip(),
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


def extract_image_url(page: Page) -> Optional[str]:
    """Not part of the original grounded extraction -- kept from a real
    improvement made directly to this script: the first image at least
    200px wide, excluding anything with "icon" in its src (filters out
    UI chrome / flag icons)."""
    try:
        images = page.locator("img").all()
        for img in images:
            width = img.get_attribute("width")
            src = img.get_attribute("src")
            if not width or not src or "icon" in src.lower():
                continue
            try:
                if int(width) >= 200:
                    return src if src.startswith("http") else f"{BASE_URL}{src}"
            except ValueError:
                continue
    except Exception as exc:
        log.debug("Image extraction failed: %s", exc)
    return None


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
    image_url = extract_image_url(page)

    return {
        "id": slug,  # PRIMARY KEY -- required, this is what on_conflict targets on upsert
        "name": name,
        "nation": nation_from_slug(slug),
        "category": category,  # NOT "type" -- must match the real column name
        "rank": rank,
        "br": br,
        "crew": crew,
        "weightTons": weight_tons,
        "armor": {"hull": hull_armor, "turret": turret_armor},
        "ammunition": ammunition,
        "imageUrl": image_url,
        "researchCostRp": research_rp,
        "purchaseCostSl": purchase_sl,
        "sourceUrl": url,
        "scrapedAt": datetime.now(timezone.utc).isoformat(),
    }


def get_supabase_client() -> SupabaseClient:
    url = os.environ.get("SUPABASE_URL")
    # SERVICE ROLE key, not anon -- this needs to bypass the public-read-only
    # RLS policy in supabase-schema.sql to write. Never use this key
    # anywhere client-facing; GitHub Actions secrets only.
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        sys.exit("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are not set. See README 'Database setup' section.")
    try:
        client = create_client(url, key)
        client.table("vehicles").select("id").limit(1).execute()  # cheap connectivity + schema check
    except Exception as exc:
        sys.exit(
            f"Could not reach the Supabase 'vehicles' table: {exc}\n"
            f"Did you run scripts/supabase-schema.sql in the Supabase SQL editor yet?"
        )
    return client


def to_supabase_row(vehicle: dict) -> dict:
    """Adapter from extract_vehicle()'s camelCase shape to
    supabase-schema.sql's snake_case columns."""
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
        "image_url": vehicle.get("imageUrl"),
        "research_cost_rp": vehicle.get("researchCostRp"),
        "purchase_cost_sl": vehicle.get("purchaseCostSl"),
        "source_url": vehicle.get("sourceUrl"),
        "scraped_at": vehicle.get("scrapedAt"),
    }


def upsert_vehicles(client: SupabaseClient, vehicles: list[dict]) -> int:
    if not vehicles:
        return 0
    rows = [to_supabase_row(v) for v in vehicles]
    # on_conflict="id" -- "id" is the actual unique/primary-key column.
    # source_url has NO unique constraint, so on_conflict="source_url"
    # (as an earlier edit of this file used) fails on every call.
    client.table("vehicles").upsert(rows, on_conflict="id").execute()
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--category", choices=list(CATEGORY_PATHS) + ["all"], default="all")
    parser.add_argument("--limit", type=int, default=None, help="cap vehicles for this run, for testing")
    parser.add_argument("--dry-run", action="store_true", help="scrape and print, skip Supabase entirely")
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

    # Fail LOUDLY rather than silently -- a run that saves zero rows must
    # never print a success message. This checks BOTH the scrape failure
    # rate AND that upserts actually happened when they should have,
    # since a schema/column bug (like the on_conflict issue this file
    # previously had) makes every scrape look "ok" while every DB write
    # silently fails underneath it.
    if stats.discovered > 0 and stats.scraped_failed / stats.discovered > 0.15:
        log.error(
            "Failure rate %.0f%% exceeds the 15%% threshold -- almost certainly a broken "
            "selector (see module docstring's 'NOT CONFIRMED' section), not bad luck.",
            100 * stats.scraped_failed / stats.discovered,
        )
        sys.exit(1)

    if db_client is not None and stats.scraped_ok > 0 and stats.upserted == 0:
        log.error("Scraped %d vehicles OK but upserted 0 -- database writes are silently failing.", stats.scraped_ok)
        sys.exit(1)

    if stats.errors:
        log.warning("First few errors:\n%s", "\n".join(stats.errors[:10]))


if __name__ == "__main__":
    main()
