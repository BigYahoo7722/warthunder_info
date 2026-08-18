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
        try:
            val = float(w_match.group(1).replace(',', ''))
            data['weight'] = val if w_match.group(2).lower() != 'kg' else val / 1000.0
        except: pass
        
    rp_match = re.search(r'(?:Research|Train|Cost)\s*[:\-]?\s*([\d\.,]+)\s*(?:RP|Points)', text_content, re.IGNORECASE)
    if rp_match: 
        try: data['rp'] = int(rp_match.group(1).replace(',', '').replace('.', ''))
        except: pass
        
    sl_match = re.search(r'(?:Purchase|Price)\s*[:\-]?\s*([\d\.,]+)\s*(?:SL|Lions|Silver)', text_content, re.IGNORECASE)
    if sl_match: 
        try: data['sl'] = int(sl_match.group(1).replace(',', '').replace('.', ''))
        except: pass
        
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
        
        context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font"] else route.continue_())
        
        page = context.new_page()
        page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
        
        urls_list = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a'))
                        .map(a => a.getAttribute('href'))
                        .filter(href => href && href.includes('/unit/'));
        }""")
        
        urls = list({f"https://wiki.warthunder.com{href}" if href.startswith("/") else href for href in urls_list})
        
        if len(urls) == 0:
            sys.exit(1)

        saved_count = 0
        for idx, url in enumerate(urls, 1):
            try:
                sys.stdout.write(f"\r[{idx}/{len(urls)}] Analyzing: {url.split('/')[-1]}... ")
                sys.stdout.flush()
                
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                
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
                    
                    // استخراج مستقیم از جدول مشخصات
                    let tableNation = "";
                    const rows = document.querySelectorAll('tr');
                    for (let row of rows) {
                        const cells = row.querySelectorAll('th, td');
                        if (cells.length >= 2) {
                            const label = cells[0].textContent.trim().toLowerCase();
                            if (label.includes('country') || label.includes('nation')) {
                                tableNation = cells[1].textContent.trim().toLowerCase();
                                break;
                            }
                        }
                    }

                    // استخراج از پاراگراف اول متنی
                    let introText = "";
                    const pTags = document.querySelectorAll('.mw-parser-output > p');
                    for (let p of pTags) {
                        if (p.textContent.trim().length > 40) {
                            introText = p.textContent.trim().toLowerCase();
                            break;
                        }
                    }
                    
                    return {
                        name: h1 ? h1.textContent.trim() : '',
                        title: document.title,
                        bodyText: document.body.innerText,
                        brText: brEl ? brEl.textContent : '',
                        image_url: imageUrl,
                        tableNation: tableNation,
                        introText: introText
                    };
                }""")
                
                text_content = page_data['bodyText']
                slug = url.split("/")[-1].lower()
                vehicle_id = slug
                
                name = page_data['name']
                if not name or "War Thunder Wiki" in name:
                    name = page_data['title'].replace(" - War Thunder Wiki", "").strip()
                    if not name or "War Thunder Wiki" in name: 
                        name = slug.replace("_", " ").title()
                
                rank_match = re.search(r'Rank\s*([IVX]+|\d+)', text_content, re.IGNORECASE)
                rank = rank_match.group(1) if rank_match else None
                if rank and not str(rank).isdigit():
                    roman_map = {'I':1, 'II':2, 'III':3, 'IV':4, 'V':5, 'VI':6, 'VII':7, 'VIII':8, 'IX':9}
                    rank = roman_map.get(rank.upper(), None)

                # ==========================================
                # موتور تشخیص کشور (استراتژی سه لایه)
                # ==========================================
                nation = "unknown"
                nations_map = {
                    'usa': 'usa', 'united states': 'usa', 'american': 'usa',
                    'ussr': 'ussr', 'soviet': 'ussr', 'russia': 'ussr', 'russian': 'ussr',
                    'britain': 'britain', 'great britain': 'britain', 'british': 'britain', 'uk': 'britain',
                    'germany': 'germany', 'german': 'germany',
                    'japan': 'japan', 'japanese': 'japan',
                    'china': 'china', 'chinese': 'china',
                    'italy': 'italy', 'italian': 'italy',
                    'france': 'france', 'french': 'france',
                    'sweden': 'sweden', 'swedish': 'sweden',
                    'israel': 'israel', 'israeli': 'israel'
                }
                
                # لایه ۱: جدول مشخصات سمت راست
                table_nat = page_data.get('tableNation', '')
                if table_nat:
                    for key, val in nations_map.items():
                        if key == table_nat or key in table_nat.split():
                            nation = val
                            break

                # لایه ۲: خواندن متن معرفی (The AH-64 is an American...)
                if nation == "unknown":
                    intro = page_data.get('introText', '')
                    for key, val in nations_map.items():
                        if f" {key} " in f" {intro} ":
                            # چک می‌کند که اسم کشور در اوایل پاراگراف باشد
                            if intro.find(key) < 150: 
                                nation = val
                                break

                # لایه ۳: اتکا به لینک
                if nation == "unknown":
                    for key, val in nations_map.items():
                        if f"_{val}" in slug or slug.endswith(val):
                            nation = val
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

                supabase.table("vehicles").upsert(vehicle_data, on_conflict="id").execute()
                saved_count += 1
                
                sys.stdout.write(f"\r{' ' * 60}\r")
                print(f"✅ Saved [{nation.upper()}]: {name}")

            except PlaywrightTimeoutError:
                continue
            except Exception as e:
                continue

        browser.close()
        print(f"\n🎉 OPERATION COMPLETE: {saved_count} vehicles perfectly integrated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", type=str, default="helicopters")
    args = parser.parse_args()
    
    run_scraper(args.category)
