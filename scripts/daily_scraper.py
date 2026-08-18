#!/usr/bin/env python3
"""
daily_scraper.py
=================
Automated daily scraper: wiki.warthunder.com -> Supabase (Postgres).
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
USER_AGENT = "war-thunder-codex-daily-scraper/1.0 (personal fan-project)"
REQUEST_DELAY_SEC = 2.0
PAGE_TIMEOUT_MS = 20_000
BATCH_SIZE = 25

CATEGORY_PATHS = {
    "aviation": "/aviation",
    "helicopters": "/helicopters",
    "army": "/ground",
    "fleet": "/ships",
}
COASTAL_FLEET_PATH = "/boats"

SLUG_PREFIX_TO_NATION = {
    "us_": "usa", "germ_": "germany", "ussr_": "ussr", "uk_": "britain",
    "jp_": "japan", "cn_": "china", "it_": "italy", "fr_": "france",
    "sw_": "sweden", "il_": "israel",
}

NATION_CLEAN_MAP = {
    "usa": "usa", "us": "usa", "united_states": "usa",
    "germany": "germany", "german": "germany",
    "ussr": "ussr", "russia": "ussr", "soviet": "ussr",
    "britain": "britain", "great_britain": "britain", "uk": "britain",
    "japan": "japan",
    "china": "china",
    "italy": "italy",
    "france": "france",
    "sweden": "sweden",
    "israel": "israel"
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


def extract_nation(page: Page, slug: str) -> Optional[str]:
    # 1. Try slug prefix first
    from_slug = nation_from_slug(slug)
    if from_slug:
        return from_slug

    # 2. Try MediaWiki categories (e.g. Category:USA_helicopters)
    try:
        cat_links = page.eval_on_selector_all(
            'a[href*="Category:"]',
            "els => els.map(e => e.getAttribute('href'))"
        )
        for href in cat_links:
            if not href:
                continue
            match = re.search(r"Category:([A-Za-z_]+)", href, re.IGNORECASE)
            if match:
                cat_name = match.group(1).lower()
                for key, val in NATION_CLEAN_MAP.items():
                    if cat_name.startswith(key):
                        return val
    except Exception:
        pass

    # 3. Search page content for nation indicators
    try:
        content = page.content().lower()
        for key, val in NATION_CLEAN_MAP.items():
            if f"category:{key}" in content or f"/{key}_" in content or f"flag_{key}" in content:
                return val
    except Exception:
        pass

    return None


def extract_rank(page: Page) -> Optional[int]:
    # 1. Direct label check
    rank_text = (text_after_label(page, "Rank") or "").strip()
    if rank_text and rank_text in RANK_ROMAN_TO_INT:
        return RANK_ROMAN_TO_INT[rank_text]

    # 2. Search body text for Roman numerals (Rank I to VIII)
    try:
        body_text = page.inner_text("body")
        match = re.search(r"\bRank\s*[:\s]*\s*(I|II|III|IV|V|VI|VII|VIII)\b", body_text, re.IGNORECASE)
        if match:
            return RANK_ROMAN_TO_INT.get(match.group(1).upper())
    except Exception:
        pass

    # 3. Search numbers 1-8
    try:
        body_text = page.inner_text("body")
        match = re.search(r"\bRank\s*[:\s]*\s*([1-8])\b", body_text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    except Exception:
        pass

    return None


def _to_float(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    cleaned = text.replace(",", "")
    match = re.search(r"[\d.]+", cleaned)
    return float(match.group(0)) if match else None


def discover_vehicle_slugs(page: Page, category: str, path: str) -> list[str]:
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
    try:
        el = page.locator(f"text='{label}'").first
        return el.locator("xpath=following-sibling::*[1]").inner_text(timeout=2000).strip()
    except (PlaywrightTimeout, Exception):
        return None


def parse_armor_triplet(text: Optional[str]) -> Optional[dict]:
    if not text:
        return None
    match = re.search(r"([\d.]+)\s*/\s*([\d.]+)\s*/\s*([\d.]+)", text)
    if not match:
        return None
    front, side, back = (float(x) for x in match.groups())
    return {"frontMm": front, "sideMm": side, "backMm": back}


def extract_ammunition(page: Page) -> list[dict]:
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

    rank = extract_rank(page)
    nation = extract_nation(page, slug)

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
        "nation": nation,
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
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        sys.exit("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are not set.")
    try:
        client = create_client(url, key)
        client.table("vehicles").select("id").limit(1).execute()
    except Exception as exc:
        sys.exit(f"Could not reach the Supabase 'vehicles' table: {exc}")
    return client


def to_supabase_row(vehicle: dict) -> dict:
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
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--category", choices=list(CATEGORY_PATHS) + ["all"], default="all")
    parser.add_argument("--limit", type=int, default=None, help="cap vehicles per category, for testing")
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
                except Exception as exc:
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

    if stats.discovered > 0 and stats.scraped_failed / stats.discovered > 0.15:
        log.error("Failure rate exceeds 15%% threshold.")
        sys.exit(1)


if __name__ == "__main__":
    main()
