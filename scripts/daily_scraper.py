import os
import re
import sys
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
# ۲. توابع هوشمند استخراج دیتا
# ==========================================
def extract_nation(page):
    nation_map = {
        'usa': 'usa', 'united states': 'usa',
        'germany': 'germany',
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
# ۳. منطق اصلی اسکرایپر (کاملاً دیباگ شده)
# ==========================================
def run_scraper(category_name):
    print(f"\n--- Starting scraper for category: {category_name} ---")
    
    category_urls = {
        'helicopters': 'https://wiki.warthunder.com/Category:Helicopters',
        'aviation': 'https://wiki.warthunder.com/Category:Aviation',
        'ground': 'https://wiki.warthunder.com/Category:Ground_vehicles'
    }
    target_url = category_urls.get(category_name.lower(), category_urls['helicopters'])

    with sync_playwright() as p:
        # شبیه‌سازی مرورگر واقعی برای فرار از Cloudflare
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        print(f"Navigating to {target_url}...")
        page.goto(target_url, wait_until="networkidle", timeout=60000)
        
        # دیباگ: چاپ تایتل صفحه برای تشخیص بلاک شدن توسط Cloudflare
        page_title = page.title()
        print(f"Page Title Loaded: '{page_title}'")
        if "Just a moment" in page_title or "Cloudflare" in page_title:
            print("❌ ERROR: Blocked by Cloudflare Anti-Bot. The scraper cannot proceed.")
            sys.exit(1)

        # صبر کردن تا لیست وسایل (div با آیدی mw-pages) لود شود
        try:
            page.wait_for_selector("#mw-pages", timeout=15000)
        except Exception:
            print("⚠️ Warning: '#mw-pages' not found! Trying to gather links anyway...")

        # جمع‌آوری هوشمندانه لینک‌ها
        raw_links = page.locator("#mw-pages a, .mw-category a, .mw-category-group a").all()
        urls = []
        for link in raw_links:
            href = link.get_attribute("href")
            if href and not href.startswith("#") and ":" not in href: # فیلتر لینک‌های نامعتبر
                full_url = f"https://wiki.warthunder.com{href}" if href.startswith("/") else href
                if full_url not in urls:
                    urls.append(full_url)
        
        print(f"✅ Found {len(urls)} vehicles to process.")

        # اگر هیچی پیدا نشد، ارور بده تا تیک سبز الکی نخوره
        if len(urls) == 0:
            print("❌ ERROR: No vehicle URLs found! Printing raw page content for debugging:")
            print(page.content()[:1000]) # چاپ ۱۰۰۰ کاراکتر اول سورس صفحه
            sys.exit(1)

        # پردازش تک تک وسایل
        for idx, url in enumerate(urls, 1):
            try:
                print(f"[{idx}/{len(urls)}] Scraping: {url}")
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                name = page.locator("h1#firstHeading").inner_text().strip()
                nation = extract_nation(page)
                rank = extract_rank(page)
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

                # ذخیره در Supabase - بروزرسانی در صورت تکراری بودن URL
                supabase.table("vehicles").upsert(vehicle_data, on_conflict="source_url").execute()

            except Exception as e:
                print(f"⚠️ Error scraping {url}: {e}")
                continue

        browser.close()
        print("\n🎉 Scraping completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="War Thunder Wiki Scraper")
    parser.add_argument("--category", type=str, default="helicopters", help="Category to scrape (helicopters, aviation, ground)")
    args = parser.parse_args()
    
    run_scraper(args.category)
