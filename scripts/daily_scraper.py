import os
import re
import sys
import json
import argparse
from playwright.sync_api import sync_playwright
from supabase import create_client, Client

# ۱. مقداردهی اولیه اتصال به دیتابیس Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables are missing.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ۲. تابع هوشمند استخراج کشور
def extract_nation(page):
    nation_map = {
        'usa': 'usa', 'us': 'usa', 'united states': 'usa',
        'germany': 'germany',
        'ussr': 'ussr', 'soviet': 'ussr', 'russia': 'ussr',
        'britain': 'britain', 'uk': 'britain', 'great britain': 'britain',
        'japan': 'japan',
        'china': 'china',
        'italy': 'italy',
        'france': 'france',
        'sweden': 'sweden',
        'israel': 'israel'
    }

    try:
        flag_imgs = page.locator(".specs_card_nation img, .general_info_nation img, .mw-parser-output img").all()
        for img in flag_imgs:
            alt_text = (img.get_attribute("alt") or "").lower()
            src_text = (img.get_attribute("src") or "").lower()
            for key, val in nation_map.items():
                if key in alt_text or key in src_text:
                    return val
    except Exception:
        pass

    try:
        categories = [cat.lower() for cat in page.locator("#mw-normal-catlinks a").all_inner_texts()]
        for cat in categories:
            for key, val in nation_map.items():
                if key in cat:
                    return val
    except Exception:
        pass

    try:
        url = page.url.lower()
        for key, val in nation_map.items():
            if f"_{key}" in url or f"/{key}" in url:
                return val
    except Exception:
        pass

    return None

# ۳. تابع هوشمند استخراج رنک (Rank)
def extract_rank(page):
    roman_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8}
    
    try:
        rank_text = page.locator(".specs_card_rank, .general_info_rank").inner_text().strip()
        match = re.search(r'Rank\s+([I|V|X]+|\d+)', rank_text, re.IGNORECASE)
        if match:
            val = match.group(1).upper()
            return roman_map.get(val, int(val) if val.isdigit() else None)
    except Exception:
        pass

    try:
        categories = page.locator("#mw-normal-catlinks a").all_inner_texts()
        for cat in categories:
            match = re.search(r'Rank\s+([I|V|X]+|\d+)', cat, re.IGNORECASE)
            if match:
                val = match.group(1).upper()
                return roman_map.get(val, int(val) if val.isdigit() else None)
    except Exception:
        pass

    return None

# ۴. تابع هوشمند استخراج وزن، RP و SL
def extract_specs_extra(page):
    text_content = ""
    try:
        text_content = page.locator(".mw-parser-output").inner_text()
    except Exception:
        pass

    weight = None
    weight_match = re.search(r'(?:Mass|Weight)[:\s]+([\d\.,]+)\s*(t|tons|kg)', text_content, re.IGNORECASE)
    if weight_match:
        try:
            val = float(weight_match.group(1).replace(',', ''))
            weight = val if weight_match.group(2).lower() != 'kg' else val / 1000.0
        except ValueError:
            pass

    rp = None
    rp_match = re.search(r'([\d\s,]+)\s*(?:RP|Research Points)', text_content)
    if rp_match:
        try:
            rp = int(rp_match.group(1).replace(',', '').replace(' ', ''))
        except ValueError:
            pass

    sl = None
    sl_match = re.search(r'([\d\s,]+)\s*(?:Silver Lions|SL)', text_content)
    if sl_match:
        try:
            sl = int(sl_match.group(1).replace(',', '').replace(' ', ''))
        except ValueError:
            pass

    return weight, rp, sl

# ۵. تابع اصلی اجرای اسکرایپر
def run_scraper(category_name):
    print(f"Starting scraper for category: {category_name}")
    
    category_urls = {
        'helicopters': 'https://wiki.warthunder.com/Category:Helicopters',
        'aviation': 'https://wiki.warthunder.com/Category:Aviation',
        'ground': 'https://wiki.warthunder.com/Category:Ground_vehicles'
    }
    
    target_url = category_urls.get(category_name.lower(), category_urls['helicopters'])

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Navigating to {target_url}...")
        page.goto(target_url, timeout=60000)
        
        # جمع‌آوری لینک تمام وسایل نقلیه
        links = page.locator(".mw-category a, .tree-item a").all()
        urls = list(set([f"https://wiki.warthunder.com{link.get_attribute('href')}" for link in links if link.get_attribute('href') and not ":" in link.get_attribute('href')]))
        
        print(f"Found {len(urls)} vehicles to process.")

        for idx, url in enumerate(urls, 1):
            try:
                print(f"[{idx}/{len(urls)}] Scraping: {url}")
                page.goto(url, timeout=30000)
                
                # ۱. نام وسیله
                name = page.locator("h1#firstHeading").inner_text().strip()
                
                # ۲. استخراج کشور و رنک
                nation = extract_nation(page)
                rank = extract_rank(page)
                
                # ۳. استخراج مشخصات تکمیلی
                weight_tons, research_cost_rp, purchase_cost_sl = extract_specs_extra(page)
                
                # ۴. استخراج Battle Rating (BR)
                br_ab, br_rb, br_sb = None, None, None
                try:
                    br_text = page.locator(".specs_card_br").inner_text()
                    br_matches = re.findall(r'\d+\.\d+|\d+', br_text)
                    if len(br_matches) >= 3:
                        br_ab, br_rb, br_sb = float(br_matches[0]), float(br_matches[1]), float(br_matches[2])
                    elif len(br_matches) >= 1:
                        br_ab = br_rb = br_sb = float(br_matches[0])
                except Exception:
                    pass

                # ۵. استخراج عکس
                image_url = None
                try:
                    img_element = page.locator(".specs_card_main_image img, .general_info_img img").first
                    if img_element.count() > 0:
                        image_url = img_element.get_attribute("src")
                        if image_url and not image_url.startswith("http"):
                            image_url = f"https://wiki.warthunder.com{image_url}"
                except Exception:
                    pass

                # ۶. ارسال داده به دیتابیس Supabase
                vehicle_data = {
                    "name": name,
                    "type": category_name.lower(),
                    "nation": nation,
                    "rank": rank,
                    "br_ab": br_ab,
                    "br_rb": br_rb,
                    "br_sb": br_sb,
                    "weight_tons": weight_tons,
                    "research_cost_rp": research_cost_rp,
                    "purchase_cost_sl": purchase_cost_sl,
                    "image_url": image_url,
                    "source_url": url
                }

                # ذخیره یا بروزرسانی بر اساس source_url
                supabase.table("vehicles").upsert(vehicle_data, on_conflict="source_url").execute()

            except Exception as e:
                print(f"Error scraping {url}: {e}")
                continue

        browser.close()
        print("Scraping completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="War Thunder Wiki Scraper")
    parser.add_argument("--category", type=str, default="helicopters", help="Category to scrape (helicopters, aviation, ground)")
    args = parser.parse_args()

    run_scraper(args.category)
