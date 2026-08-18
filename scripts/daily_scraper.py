import os
import sys
import re
import argparse
from playwright.sync_api import sync_playwright
from supabase import create_client, Client

# ==========================================
# ۱. اتصال به دیتابیس Supabase
# ==========================================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables are missing.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# ۲. توابع استخراج دیتا
# ==========================================
def extract_nation(page):
    nation_map = {
        'usa': 'usa', 'united states': 'usa', 'germany': 'germany',
        'ussr': 'ussr', 'soviet': 'ussr', 'russia': 'ussr',
        'britain': 'britain', 'uk': 'britain', 'great britain': 'britain',
        'japan': 'japan', 'china': 'china', 'italy': 'italy',
        'france': 'france', 'sweden': 'sweden', 'israel': 'israel'
    }
    try:
        flag_imgs = page.locator(".specs_card_nation img, .general_info_nation img, .mw-parser-output img").all()
        for img in flag_imgs:
            text = ((img.get_attribute("alt") or "") + " " + (img.get_attribute("src") or "")).lower()
            for key, val in nation_map.items():
                if key in text: return val
    except: pass
    return None

def extract_rank(page):
    roman_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8}
    try:
        rank_text = page.locator(".specs_card_rank, .general_info_rank").inner_text().strip()
        match = re.search(r'Rank\s+([I|V|X]+|\d+)', rank_text, re.IGNORECASE)
        if match: return roman_map.get(match.group(1).upper(), int(match.group(1)) if match.group(1).isdigit() else None)
    except: pass
    return None

def extract_specs_extra(page):
    weight, rp, sl = None, None, None
    try:
        text_content = page.locator(".mw-parser-output").inner_text()
        w_match = re.search(r'(?:Mass|Weight)[:\s]+([\d\.,]+)\s*(t|tons|kg)', text_content, re.IGNORECASE)
        if w_match:
            val = float(w_match.group(1).replace(',', ''))
            weight = val if w_match.group(2).lower() != 'kg' else val / 1000.0
            
        rp_match = re.search(r'([\d\s,]+)\s*(?:RP|Research Points)', text_content)
        if rp_match: rp = int(rp_match.group(1).replace(',', '').replace(' ', ''))
            
        sl_match = re.search(r'([\d\s,]+)\s*(?:Silver Lions|SL)', text_content)
        if sl_match: sl = int(sl_match.group(1).replace(',', '').replace(' ', ''))
    except: pass
    return weight, rp, sl

# ==========================================
# ۳. منطق اصلی اسکرایپر (با بالاترین انعطاف‌پذیری)
# ==========================================
def run_scraper(category_name):
    print(f"\n--- Starting smart scraper for category: {category_name} ---")
    
    # سیستم جستجوی مسیر (Fallback URLs): ربات آدرس‌های مختلف را تست می‌کند تا مسیر درست را بیابد
    category_fallbacks = {
        'helicopters': [
            'https://wiki.warthunder.com/Helicopters',
            'https://wiki.warthunder.com/Category:Helicopters',
            'https://wiki.warthunder.com/Portal:Helicopters'
        ],
        'aviation': [
            'https://wiki.warthunder.com/Aviation',
            'https://wiki.warthunder.com/Category:Aviation',
            'https://wiki.warthunder.com/Portal:Aviation'
        ],
        'ground': [
            'https://wiki.warthunder.com/Ground_vehicles',
            'https://wiki.warthunder.com/Category:Ground_vehicles',
            'https://wiki.warthunder.com/Portal:Ground_vehicles'
        ]
    }
    
    target_urls = category_fallbacks.get(category_name.lower(), category_fallbacks['helicopters'])

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        valid_page_found = False
        
        # تست کردن آدرس‌ها تا رسیدن به صفحه معتبر
        for url in target_urls:
            print(f"Testing URL: {url}...")
            try:
                response = page.goto(url, wait_until="domcontentloaded", timeout=45000)
                if response and response.status == 200 and "Page not found" not in page.title():
                    print(f"✅ Successfully loaded entry page: {url}")
                    valid_page_found = True
                    break
            except Exception as e:
                print(f"⚠️ Failed to load {url}: {e}")
                
        if not valid_page_found:
            print("❌ ERROR: All fallback URLs failed. The website structure might have drastically changed.")
            sys.exit(1)

        # استخراج گسترده لینک‌ها
        try:
            page.wait_for_selector(".mw-parser-output, #mw-pages, .tree-item", timeout=15000)
        except Exception:
            pass

        raw_links = page.locator("a").all()
        urls = set()
        
        # فیلتر ضد-آشغال (فقط لینک‌های معتبر ویکی را نگه می‌دارد)
        bad_namespaces = ["Category:", "Special:", "File:", "User:", "Template:", "Talk:", "Help:", "Portal:", "Update:", "News:"]
        
        for link in raw_links:
            href = link.get_attribute("href")
            if href and href.startswith("/"):
                # بررسی اینکه لینک حاوی صفحات نامعتبر نباشد
                is_valid = True
                for bad_ns in bad_namespaces:
                    if f"/{bad_ns}" in href:
                        is_valid = False
                        break
                
                if is_valid and ":" not in href.split("/")[-1]:
                    urls.add(f"https://wiki.warthunder.com{href}")
        
        urls = list(urls)
        print(f"✅ Found {len(urls)} potential links to inspect.")

        if len(urls) == 0:
            print("❌ ERROR: No links extracted. Something is blocking the scraper.")
            sys.exit(1)

        saved_count = 0
        for idx, url in enumerate(urls, 1):
            try:
                print(f"[{idx}/{len(urls)}] Checking: {url}")
                response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # اگر ریدایرکت شد یا صفحه 404 بود، رد شو
                if response and response.status != 200:
                    continue
                
                # تأییدیه اصالت: اگر جدول مشخصات (Specs Card) نداشت، یعنی وسیله نقلیه نیست!
                if page.locator(".specs_card_main_info, .specs_card_main_image, .general_info_blocks").count() == 0:
                    print("   ↪ Skipped: Not a valid vehicle page (No specs card found).")
                    continue

                name_locator = page.locator("h1#firstHeading")
                if name_locator.count() == 0:
                    continue
                name = name_locator.inner_text().strip()
                
                nation = extract_nation(page)
                rank = extract_rank(page)
                
                if nation is None and rank is None:
                    continue
                
                weight_tons, research_cost_rp, purchase_cost_sl = extract_specs_extra(page)
                
                br_ab, br_rb, br_sb = None, None, None
                try:
                    br_text = page.locator(".specs_card_br").inner_text()
                    br_matches = re.findall(r'\d+\.\d+|\d+', br_text)
                    if len(br_matches) >= 3:
                        br_ab, br_rb, br_sb = float(br_matches[0]), float(br_matches[1]), float(br_matches[2])
                    elif len(br_matches) >= 1:
                        br_ab = br_rb = br_sb = float(br_matches[0])
                except: pass

                image_url = None
                try:
                    img_element = page.locator(".specs_card_main_image img, .general_info_img img").first
                    if img_element.count() > 0:
                        image_url = img_element.get_attribute("src")
                        if image_url and not image_url.startswith("http"):
                            image_url = f"https://wiki.warthunder.com{image_url}"
                except: pass

                vehicle_data = {
                    "name": name, "type": category_name.lower(), "nation": nation,
                    "rank": rank, "br_ab": br_ab, "br_rb": br_rb, "br_sb": br_sb,
                    "weight_tons": weight_tons, "research_cost_rp": research_cost_rp,
                    "purchase_cost_sl": purchase_cost_sl, "image_url": image_url,
                    "source_url": url
                }

                # ذخیره ایمن در دیتابیس
                supabase.table("vehicles").upsert(vehicle_data, on_conflict="source_url").execute()
                saved_count += 1
                print(f"   ✓ Saved: {name} ({nation.capitalize()} - Rank {rank})")

            except Exception as e:
                print(f"⚠️ Error scraping {url}: {e}")
                continue

        browser.close()
        print(f"\n🎉 Scraping completed successfully! {saved_count} verified vehicles saved/updated in the database.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="War Thunder Wiki Scraper")
    parser.add_argument("--category", type=str, default="helicopters", help="Category to scrape (helicopters, aviation, ground)")
    args = parser.parse_args()
    
    run_scraper(args.category)
