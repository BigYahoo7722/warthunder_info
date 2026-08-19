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
log = logging.getLogger("immortal-scraper")

BASE_URL = "https://wiki.warthunder.com"
USER_AGENT = "war-thunder-codex-immortal-bot/3.0"
REQUEST_DELAY_SEC = 1.5 
PAGE_TIMEOUT_MS = 30_000 # افزایش تایم‌اوت برای جلوگیری از کرش در اینترنت ضعیف
BATCH_SIZE = 20

CATEGORY_PATHS = {
    "aviation": "/aviation",
    "helicopters": "/helicopters",
    "army": "/ground",
    "fleet": "/ships",
}
COASTAL_FLEET_PATH = "/boats"

# دیکشنری فوق‌کامل برای تشخیص ۱۰۰٪ ملیت‌ها از روی اسلاگ (لینک)
SLUG_PREFIX_TO_NATION = {
    "us_": "USA", "germ_": "Germany", "ussr_": "USSR", "su_": "USSR", 
    "uk_": "Britain", "gb_": "Britain", "jp_": "Japan", "cn_": "China", 
    "it_": "Italy", "fr_": "France", "sw_": "Sweden", "il_": "Israel",
    "za_": "South Africa", "fi_": "Finland", "hu_": "Hungary"
}

RANK_ROMAN_TO_INT = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8}

@dataclass
class ScrapeStats:
    discovered: int = 0
    upserted: int = 0
    errors: list[str] = field(default_factory=list)

def get_nation_smart(slug: str, dynamic_data: dict) -> str:
    # ۱. اول از همه از دیکشنری لینک‌ها می‌خونیم
    for prefix, nation in SLUG_PREFIX_TO_NATION.items():
        if slug.lower().startswith(prefix):
            return nation
    
    # ۲. اگه تو لینک نبود، می‌گردیم تو دیتای داینامیکی که از جدول سایت درآوردیم
    if "country" in dynamic_data:
        return dynamic_data["country"].title()
        
    return "Unknown" # هیچوقت ارور نمیده، نهایتا میزنه نامشخص

def _to_float(text: Optional[str]) -> Optional[float]:
    if not text: return None
    match = re.search(r"[\d.]+", text.replace(",", ""))
    return float(match.group(0)) if match else None

def extract_vehicle_smart(page: Page, slug: str, category: str) -> Optional[dict]:
    url = f"{BASE_URL}/unit/{slug}"
    try:
        page.goto(url, timeout=PAGE_TIMEOUT_MS, wait_until="domcontentloaded")
    except Exception as e:
        log.warning(f"Timeout/Error loading {url}: {e}")
        return None
    
    time.sleep(REQUEST_DELAY_SEC)

    # تزریق جاوااسکریپت برای استخراج فوق‌هوشمند (Self-Healing Extraction)
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

            // استخراج عکس اصلی مستقیما از متاتگ سئو (قوی‌ترین روش)
            let ogImage = document.querySelector('meta[property="og:image"]');
            let imgUrl = ogImage ? ogImage.content : null;
            
            // روش بک‌آپ برای عکس اگه سئو نداشت
            if (!imgUrl) {
                let fallbackImg = document.querySelector('.image img');
                imgUrl = fallbackImg ? fallbackImg.src : null;
            }

            return {
                title: document.title,
                h1: document.querySelector('h1') ? document.querySelector('h1').innerText : '',
                imageUrl: imgUrl,
                dynamicData: dynamicData
            };
        }""")
    except Exception as e:
        log.error(f"JS extraction failed on {slug}: {e}")
        page_data = {"h1": "", "title": "", "imageUrl": None, "dynamicData": {}}

    name = re.sub(r'[\-\|]?\s*War Thunder.*$', '', page_data['h1'] or page_data['title']).strip()
    if not name: name = slug.replace("_", " ").title()

    nation = get_nation_smart(slug, page_data.get("dynamicData", {}))
    
    # اطمینان از فرمت لینک عکس
    img_url = page_data.get("imageUrl")
    if img_url and str(img_url).startswith('/'):
        img_url = f"{BASE_URL}{img_url}"

    rank_val = RANK_ROMAN_TO_INT.get(page_data['dynamicData'].get('rank', 'I'))

    return {
        "id": slug,
        "name": name,
        "nation": nation,
        "category": category,
        "rank": rank_val,
        "imageUrl": img_url,
        "sourceUrl": url,
        "scrapedAt": datetime.now(timezone.utc).isoformat(),
        "dynamicSpecs": page_data.get("dynamicData", {})
    }

def get_supabase_client() -> SupabaseClient:
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])

def upsert_vehicles(client: SupabaseClient, vehicles: list[dict]) -> int:
    if not vehicles: return 0
    rows = []
    for v in vehicles:
        rows.append({
            "id": v["id"],
            "name": v["name"],
            "nation": v["nation"],
            "category": v["category"],
            "rank": v["rank"],
            "image_url": v.get("imageUrl"),
            "source_url": v["sourceUrl"],
            "scraped_at": v["scrapedAt"],
            "dynamic_specs": v.get("dynamicSpecs", {})
        })
    # قانون «اگه نبود بساز، اگه بود فقط آپدیت کن»
    client.table("vehicles").upsert(rows, on_conflict="id").execute()
    return len(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", required=True)
    args = parser.parse_args()

    client = get_supabase_client()
    stats = ScrapeStats()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(user_agent=USER_AGENT)
        page = context.new_page()

        paths = [CATEGORY_PATHS[args.category]] if args.category in CATEGORY_PATHS else []
        if args.category == "fleet": paths.append(COASTAL_FLEET_PATH)

        slugs = []
        for path in paths:
            page.goto(f"{BASE_URL}{path}", wait_until="domcontentloaded")
            elements = page.eval_on_selector_all('a[href*="/unit/"]', "els => els.map(e => e.getAttribute('href'))")
            slugs.extend([e.rsplit("/unit/", 1)[-1].split("?")[0] for e in elements if "/unit/" in e])
        
        slugs = sorted(list(set(slugs)))
        stats.discovered = len(slugs)

        batch = []
        for i, slug in enumerate(slugs, 1):
            log.info(f"[{args.category} {i}/{len(slugs)}] Processing {slug}...")
            vehicle = extract_vehicle_smart(page, slug, args.category)
            if vehicle:
                batch.append(vehicle)
            
            if len(batch) >= BATCH_SIZE:
                stats.upserted += upsert_vehicles(client, batch)
                batch.clear()

        if batch:
            stats.upserted += upsert_vehicles(client, batch)

        browser.close()
    
    log.info(f"Mission Complete! Discovered: {stats.discovered} | Saved/Updated: {stats.upserted}")

if __name__ == "__main__":
    main()
