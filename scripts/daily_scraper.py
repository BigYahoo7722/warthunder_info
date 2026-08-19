#!/usr/bin/env python3
"""
daily_scraper.py
=================
Automated scraper: wiki.warthunder.com -> Supabase (Postgres).
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
USER_AGENT = "war-thunder-codex-daily-scraper/2.0 (personal fan-project)"
# زمان تاخیر روی 1.5 تنظیم شد تا هواپیماها به لیمیت 6 ساعته گیت‌هاب اکشن نخورند
REQUEST_DELAY_SEC = 1.5 
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


def extract_image_url(page: Page) -> Optional[str]:
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

    # استخراج دیتای داینامیک از جدول‌های سایت با جاوااسکریپت
    try:
        page_data = page.evaluate(r"""() => {
            const infoRows = Array.from(document.querySelectorAll('.infobox tr, .specs-card tr'));
            let dynamicData = {};
            infoRows.forEach(row => {
                const th = row.querySelector('th');
                const td = row.querySelector('td');
                if (th && td) {
                    let key = th.innerText.trim().replace(/[^a-zA-Z0-9 ]/g, "").replace(/\s+/g, "_").toLowerCase();
                    let value = td.innerText.trim();
                    if (key && value) {
                        dynamicData[key] = value;
                    }
                }
            });

            return {
                title: document.title,
                h1: document.querySelector('h1') ? document.querySelector('h1').textContent : '',
                imageUrl: Array.from(document.querySelectorAll('img'))
                    .map(img => img.getAttribute('src'))
                    .find(src => src && !src.includes('icon') && document.querySelector(`img[src="${src}"]`).getAttribute('width') >= 200) || null,
                dynamicData: dynamicData
            };
        }""")
    except Exception as e:
        log.warning("JS evaluation failed for %s: %s", slug, e)
        page_data = {"h1": "", "title": "", "imageUrl": None, "dynamicData": {}}

    raw_name = page_data['h1'].strip() or page_data['title'].strip()
    name = re.sub(r'[\-\|]?\s*War Thunder.*$', '', raw_name, flags=re.IGNORECASE).strip()
    if not name:
        name = slug.replace("_", " ").title()

    image_url = page_data['imageUrl']
    if image_url and image_url.startswith('/'):
        image_url = f"{BASE_URL}{image_url}"
    elif not image_url:
        image_url = extract_image_url(page)

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
        "imageUrl": image_url,
        "researchCostRp": research_rp,
        "purchaseCostSl": purchase_sl,
        "sourceUrl": url,
        "scrapedAt": datetime.now(timezone.utc).isoformat(),
        "dynamicSpecs": page_data.get("dynamicData", {}) # دیتای هوشمند
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
    # مپ کردن دیتا به همراه مقدار پیش‌فرض تا از کرش جلوگیری شود
    return {
        "id": vehicle["id"],
        "name": vehicle.get("name") or vehicle["id"].replace("_", " ").title(),
        "nation": vehicle.get("nation"),
        "category": vehicle["category"],
        "rank": vehicle.get("rank"),
        "br_ab": br.get("ab"),
        "br_rb": br.get("rb"),
        "br_sb": br.get("sb"),
        "crew": vehicle.get("crew"),
        "weight_tons": vehicle.get("weightTons"),
        "armor": vehicle.get("armor") or {},
        "ammunition": vehicle.get("ammunition") or [],
        "image_url": vehicle.get("imageUrl"),
        "research_cost_rp": vehicle.get("researchCostRp"),
        "purchase_cost_sl": vehicle.get("purchaseCostSl"),
        "source_url": vehicle.get("sourceUrl"),
        "scraped_at": vehicle.get("scrapedAt"),
        "dynamic_specs": vehicle.get("dynamicSpecs") or {} # تزریق اطلاعات جانبی و داینامیک
    }


def upsert_vehicles(client: SupabaseClient, vehicles: list[dict]) -> int:
    if not vehicles:
        return 0
    rows = [to_supabase_row(v) for v in vehicles]
    # ذخیره و به‌روزرسانی هوشمند دیتابیس (اگر بود آپدیت کن، اگر نبود بساز)
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
