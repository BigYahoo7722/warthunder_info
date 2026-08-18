import os
import sys
import re
import argparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from supabase import create_client, Client

# ==========================================
# ۱. اتصال به دیتابیس Supabase
# ==========================================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing.")
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

def extract_br_smart(br_text, text_content):
    if br_text:
        matches = re.findall(r'\d+\.\d+|\d+', br_text)
        if len(matches) >= 3: return float(matches[0]), float(matches[1]), float(matches[2])
        elif len(matches) >= 1: return float(matches[0]), float(matches[0]), float(matches[0])
    
    matches = re.findall(r'Battle Rating\s*[:\-]?\s*(\d+\.\d+|\d+)', text_content, re.IGNORECASE)
    if matches:
        val = float(matches[0])
        return val, val, val
    return None, None, None

# ==========================================
# ۳. خزنده اصلی (TURBO)
# ==========================================
def run_scraper(category_input):
    cat_lower = category_input.lower()
    print(f"\n--- Starting Next-Gen TURBO Scraper for: {cat_lower} ---")
    
    category_fallbacks = {
        'army': 'https://wiki.warthunder.com/ground',
        'ground': 'https://wiki.warthunder.com/ground',
        'aviation': 'https://wiki.warthunder.com/aviation',
        'fleet': 'https://wiki.warthunder.com/fleet',
        'helicopters': 'https://wiki.warthunder.com/helicopters'
    }
    
    if cat_lower not in category_fallbacks:
        print(f"❌ Error: Invalid category '{category_input}'. Choose from {list(category_fallbacks.keys())}")
        sys.exit(1)
        
    target_url = category_fallbacks[cat_lower]
    db_category = 'ground' if cat_lower == 'army' else cat_lower

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        
        # مسدودسازی منابع سنگین برای بالاترین سرعت ممکن
        context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font"] else route.continue_())
        
        page = context.new_page()
        
        print(f"Loading main category page: {target_url}")
        page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
        
        urls_list = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a'))
                        .map(a => a.getAttribute('href'))
                        .filter(href => href && href.includes('/unit/'));
        }""")
        
        urls = set()
        for href in urls_list:
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
                sys.stdout.write(f"\r[{idx}/{len(urls)}] Analyzing: {url.split('/')[-1]}... ")
                sys.stdout.flush()
                
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                
                # استخراج اطلاعات جامع + دسته‌بندی‌های سایت برای تشخیص دقیق کشور
                page_data = page.evaluate("""() => {
                    const h1 = document.querySelector('h1');
                    const brEl = document.querySelector('.specs_card_br, .br-value');
                    
                    let imageUrl = null;
                    const imgs = Array.from(document.querySelectorAll('img'));
                    for (let img of imgs) {
                        const w = img.getAttribute('width');
                        const src = img.getAttribute('src');
                        if (w && parseInt(w) >= 200 && src && !src.toLowerCase().includes('icon')) {
                            imageUrl = src.startsWith('/') ? 'https://wiki.warthunder.com' + src : src;
                            break;
                        }
                    }
                    
                    const catLinks = Array.from(document.querySelectorAll('.mw-normal-catlinks a, #mw-normal-catlinks a')).map(a => a.innerText.toLowerCase());
                    
                    return {
                        name: h1 ? h1.innerText.trim() : '',
                        title: document.title,
                        bodyText: document.body.innerText,
                        brText: brEl ? brEl.innerText : '',
                        image_url: imageUrl,
                        categories: catLinks
                    };
                }""")
                
                text_content = page_data['bodyText']
                slug = url.split("/")[-1].lower()
                vehicle_id = slug
                
                name = page_data['name']
                if not name or "War Thunder Wiki" in name:
                    name_from_url = slug.replace("_", " ").title()
                    name = page_data['title'].replace(" - War Thunder Wiki", "").strip()
                    if not name or "War Thunder Wiki" in name: 
                        name = name_from_url
                
                rank_match = re.search(r'Rank\s*([IVX]+|\d+)', text_content, re.IGNORECASE)
                rank = rank_match.group(1) if rank_match else None
                if rank and not str(rank).isdigit():
                    roman_map = {'I':1, 'II':2, 'III':3, 'IV':4, 'V':5, 'VI':6, 'VII':7, 'VIII':8, 'IX':9}
                    rank = roman_map.get(rank.upper(), None)

                # ==========================================
                # سیستم هوشمند سه‌لایه برای استخراج کشور
                # ==========================================
                nation = "unknown"
                
                # لایه ۱: چک کردن پیشوندهای کلاسیک (بیشتر برای تانک‌ها)
                nation_prefixes = {
                    'us_': 'usa', 'germ_': 'germany', 'ussr_': 'ussr', 'uk_': 'britain',
                    'jp_': 'japan', 'cn_': 'china', 'it_': 'italy', 'fr_': 'france',
                    'sw_': 'sweden', 'il_': 'israel'
                }
                for prefix, nat in nation_prefixes.items():
                    if slug.startswith(prefix) or f"_{prefix}" in slug:
                        nation = nat
                        break
                
                # لایه ۲: چک کردن وجود نام کامل کشور در اسلاگ (مثل ah_64e_china)
                nations_list = ['usa', 'germany', 'ussr', 'britain', 'japan', 'china', 'italy', 'france', 'sweden', 'israel']
                if nation == "unknown":
                    for nat in nations_list:
                        if f"_{nat}" in slug or slug.endswith(nat):
                            nation = nat
                            break

                # لایه ۳ (تیر خلاص): چک کردن دسته‌بندی‌های رسمی خود ویکی وار تاندر
                if nation == "unknown":
                    cat_map = {
                        'usa': 'usa', 'united states': 'usa',
                        'germany': 'germany',
                        'ussr': 'ussr', 'soviet': 'ussr', 'russia': 'ussr',
                        'britain': 'britain', 'great britain': 'britain',
                        'japan': 'japan',
                        'china': 'china',
                        'italy': 'italy',
                        'france': 'france',
                        'sweden': 'sweden',
                        'israel': 'israel'
                    }
                    for cat in page_data.get('categories', []):
                        for key, nat in cat_map.items():
                            if key in cat:
                                nation = nat
                                break
                        if nation != "unknown":
                            break
                
                semantic_data = extract_semantic_data(text_content)
                br_ab, br_rb, br_sb = extract_br_smart(page_data['brText'], text_content)

                vehicle_data = {
                    "id": vehicle_id,
                    "name": name, 
                    "category": db_category, 
                    "nation": nation,
                    "rank": rank, 
                    "br_ab": br_ab, "br_rb": br_rb, "br_sb": br_sb,
                    "weight_tons": semantic_data['weight'], 
                    "research_cost_rp": semantic_data['rp'],
                    "purchase_cost_sl": semantic_data['sl'], 
                    "image_url": page_data['image_url'],
                    "source_url": url
                }

                # ذخیره در دیتابیس
                supabase.table("vehicles").upsert(vehicle_data, on_conflict="id").execute()
                saved_count += 1
                
                # با فاصله‌ی خالی، خط قبلی (Analyzing...) را به طور کامل پاک می‌کنیم تا لاگ تمیز بماند
                sys.stdout.write(f"\r{' ' * 60}\r")
                print(f"✅ Saved [{nation.upper()}]: {name}")

            except PlaywrightTimeoutError:
                sys.stdout.write(f"\r{' ' * 60}\r")
                print(f"⚠️ Timeout (skipped): {url.split('/')[-1]}")
                continue
            except Exception as e:
                sys.stdout.write(f"\r{' ' * 60}\r")
                print(f"⚠️ Error on {url.split('/')[-1]}: {str(e)[:50]}")
                continue

        browser.close()
        
        if saved_count == 0:
            print("\n❌ CRITICAL ERROR: 0 vehicles were saved successfully.")
            sys.exit(1)
            
        print(f"\n🎉 OPERATION COMPLETE: {saved_count} vehicles perfectly integrated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", type=str, default="helicopters")
    args = parser.parse_args()
    
    run_scraper(args.category)
