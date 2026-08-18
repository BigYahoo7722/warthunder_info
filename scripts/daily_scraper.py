import os
import sys
import re
import time
import argparse
from playwright.sync_api import sync_playwright
from supabase import create_client, Client

# ==========================================
# ۱. اتصال به دیتابیس Supabase
# ==========================================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# ۲. سیستم استخراج معنایی دیتا
# ==========================================
def extract_semantic_data(text_content):
    data = {'weight': None, 'rp': None, 'sl': None}
    
    w_match = re.search(r'(?:Mass|Weight|Max takeoff weight)\s*[:\-]?\s*([\d\.,]+)\s*(t|tons|kg)', text_content, re.IGNORECASE)
    if w_match:
        val = float(w_match.group(1).replace(',', ''))
        data['weight'] = val if w_match.group(2).lower() != 'kg' else val / 1000.0
        
    rp_match = re.search(r'(?:Research|Train|Cost)\s*[:\-]?\s*([\d\.,]+)\s*(?:RP|Points)', text_content, re.IGNORECASE)
    if rp_match: 
        data['rp'] = int(rp_match.group(1).replace(',', '').replace('.', ''))
        
    sl_match = re.search(r'(?:Purchase|Price)\s*[:\-]?\s*([\d\.,]+)\s*(?:SL|Lions|Silver)', text_content, re.IGNORECASE)
    if sl_match: 
        data['sl'] = int(sl_match.group(1).replace(',', '').replace('.', ''))
        
    return data

def extract_br_smart(page, text_content):
    try:
        br_text = page.locator(".specs_card_br, .br-value").inner_text(timeout=1000)
        matches = re.findall(r'\d+\.\d+|\d+', br_text)
        if len(matches) >= 3: return float(matches[0]), float(matches[1]), float(matches[2])
        elif len(matches) >= 1: return float(matches[0]), float(matches[0]), float(matches[0])
    except: pass
    
    matches = re.findall(r'Battle Rating\s*[:\-]?\s*(\d+\.\d+|\d+)', text_content, re.IGNORECASE)
    if matches:
        val = float(matches[0])
        return val, val, val
    return None, None, None

# ==========================================
# ۳. خزنده اصلی (هماهنگ با ساختار جدید /unit/)
# ==========================================
def run_scraper(category_name):
    print(f"\n--- Starting Next-Gen Scraper for: {category_name} ---")
    
    # آدرس اصلی دسته‌بندی‌ها
    category_fallbacks = {
        'helicopters': 'https://wiki.warthunder.com/Helicopters',
        'aviation': 'https://wiki.warthunder.com/Aviation',
        'ground': 'https://wiki.warthunder.com/Ground_vehicles'
    }
    target_url = category_fallbacks.get(category_name.lower(), category_fallbacks['helicopters'])

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # باز کردن صفحه دسته‌بندی برای پیدا کردن لینک‌ها
        print(f"Loading main category page: {target_url}")
        page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
        try: page.wait_for_timeout(2000) # صبر برای رندر شدن لینک‌ها
        except: pass
        
        raw_links = page.locator("a").all()
        urls = set()
        
        for link in raw_links:
            href = link.get_attribute("href")
            # تغییر کلیدی: فقط لینک‌هایی که شامل /unit/ هستند رو برمی‌داره
            if href and "/unit/" in href:
                full_url = f"https://wiki.warthunder.com{href}" if href.startswith("/") else href
                urls.add(full_url)
        
        urls = list(urls)
        print(f"✅ Found {len(urls)} EXACT vehicle links (/unit/ format).")

        if len(urls) == 0:
            print("❌ No /unit/ links found. Exiting.")
            sys.exit(1)

        saved_count = 0
        for idx, url in enumerate(urls, 1):
            try:
                print(f"[{idx}/{len(urls)}] Analyzing: {url}")
                # استفاده از networkidle برای لود شدن کامل ساختار جدید سایت
                page.goto(url, wait_until="networkidle", timeout=30000)
                
                text_content = page.inner_text("body")
                
                # استخراج هوشمندانه اسم از URL اگر صفحه تایتل درست نداشت
                name_from_url = url.split("/")[-1].replace("_", " ").title()
                name = page.title().replace(" - War Thunder Wiki", "").strip()
                if not name or "War Thunder Wiki" in name: 
                    name = name_from_url
                
                # استخراج رنک
                rank_match = re.search(r'Rank\s*([IVX]+|\d+)', text_content, re.IGNORECASE)
                rank = rank_match.group(1) if rank_match else None
                if rank and not str(rank).isdigit():
                    roman_map = {'I':1, 'II':2, 'III':3, 'IV':4, 'V':5, 'VI':6, 'VII':7, 'VIII':8, 'IX':9}
                    rank = roman_map.get(rank.upper(), None)

                # استخراج کشور (تشخیص از روی URL و متن)
                nations = ['usa', 'germany', 'ussr', 'britain', 'japan', 'china', 'italy', 'france', 'sweden', 'israel']
                nation = None
                text_lower = text_content.lower()
                for n in nations:
                    if f"_{n}" in url.lower() or f"nation: {n}" in text_lower or f"country: {n}" in text_lower:
                        nation = n
                        break
                if not nation: nation = "unknown"
                
                semantic_data = extract_semantic_data(text_content)
                br_ab, br_rb, br_sb = extract_br_smart(page, text_content)
                
                # استخراج تصویر
                image_url = None
                try:
                    images = page.locator("img").all()
                    for img in images:
                        w = img.get_attribute("width")
                        if w and int(w) >= 200:
                            src = img.get_attribute("src")
                            if src and "icon" not in src.lower():
                                image_url = f"https://wiki.warthunder.com{src}" if src.startswith("/") else src
                                break
                except: pass

                vehicle_data = {
                    "name": name, 
                    "type": category_name.lower(), 
                    "nation": nation,
                    "rank": rank, 
                    "br_ab": br_ab, "br_rb": br_rb, "br_sb": br_sb,
                    "weight_tons": semantic_data['weight'], 
                    "research_cost_rp": semantic_data['rp'],
                    "purchase_cost_sl": semantic_data['sl'], 
                    "image_url": image_url,
                    "source_url": url
                }

                # ذخیره در دیتابیس
                supabase.table("vehicles").upsert(vehicle_data, on_conflict="source_url").execute()
                saved_count += 1
                print(f"   ✓ Saved: {name}")
                
                # وقفه کوتاه برای جلوگیری از فشار به سرور
                time.sleep(1)

            except Exception as e:
                print(f"⚠️ Error on {url}: {e}")
                continue

        browser.close()
        print(f"\n🎉 OPERATION COMPLETE: {saved_count} vehicles perfectly integrated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", type=str, default="helicopters")
    args = parser.parse_args()
    
    run_scraper(args.category)
