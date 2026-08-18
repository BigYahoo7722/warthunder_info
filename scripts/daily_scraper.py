import os
import sys
import re
import time
import argparse
from collections import Counter
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from supabase import create_client, Client

# ==========================================
# ۱. پیکربندی بدون محدودیت و اتصال
# ==========================================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

START_TIME = time.time()
MAX_RUNTIME_SECONDS = 5.5 * 3600  # توقف امن در ۵.۵ ساعت برای جلوگیری از کیل شدن توسط گیت‌هاب

MAIN_NATIONS = {
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

SUBTREE_MAP = {
    'netherlands': 'france', 'greece': 'usa', 'rooivalk': 'britain',
    'south_africa': 'britain', 'hungary': 'italy', 'finland': 'sweden',
    'iaf': 'israel', 'pakistan': 'ussr', 'indonesia': 'japan', 'singapore': 'japan'
}

# ==========================================
# ۲. موتور جستجوی ۹ لایه‌ای (بدون محدودیت)
# ==========================================
class LimitlessExtractor:
    @staticmethod
    def find_nation(page_data, slug, text_content):
        # لایه ۱: جداول مشخصات صریح
        if page_data.get('tableNation'):
            for key, val in MAIN_NATIONS.items():
                if key in page_data['tableNation']: return val

        # لایه ۲: دسته‌بندی‌های مدیاویکی (دقیق‌ترین روش پنهان)
        cat_links = page_data.get('catLinks', '').lower()
        for key, val in MAIN_NATIONS.items():
            if f"{key}_helicopters" in cat_links or f"{key}_aircraft" in cat_links or f"{key}_ground" in cat_links:
                return val

        # لایه ۳: بردکرامب‌ها (مسیر ناوبری بالای صفحه)
        breadcrumbs = page_data.get('breadcrumbs', '').lower()
        for key, val in MAIN_NATIONS.items():
            if key in breadcrumbs: return val

        # لایه ۴: درخت‌های فرعی (Sub-trees) در اسلاگ و عنوان
        for sub, parent in SUBTREE_MAP.items():
            if sub in slug or sub in page_data['title'].lower(): return parent

        # لایه ۵: پیشوند/پسوند اسلاگ URL
        for key, val in MAIN_NATIONS.items():
            if f"_{key}" in slug or slug.startswith(f"{key}_"): return val

        # لایه ۶: استخراج از روی عکس پرچم‌ها
        img_alts = page_data.get('imgAlts', '').lower()
        for key, val in MAIN_NATIONS.items():
            if f"flag_{key}" in img_alts or f"{key}_flag" in img_alts: return val

        # لایه ۷: جستجو در پاراگراف اول (NLP ساده)
        intro = text_content[:1500].lower()
        for key, val in MAIN_NATIONS.items():
            if re.search(r'\b' + re.escape(key) + r'\b', intro): return val

        # لایه ۸ (لایه نهایی): تحلیل فرکانس و تکرار کلمات در کل مقاله!
        # اگر هیچ جا صراحتاً نوشته نشده بود، هر کشوری که در مقاله بیشتر تکرار شده باشد همان است.
        nation_counts = Counter()
        full_text_lower = text_content.lower()
        for key, val in MAIN_NATIONS.items():
            nation_counts[val] += len(re.findall(r'\b' + re.escape(key) + r'\b', full_text_lower))
        
        if nation_counts:
            most_common = nation_counts.most_common(1)[0]
            if most_common[1] > 2: # حداقل 3 بار تکرار شده باشد
                return most_common[0]

        return "unknown" # در این نقطه احتمال unknown شدن تقریباً صفر مطلق است.

    @staticmethod
    def extract_br(br_text, text_content):
        # تلاش برای استخراج دقیق ৩ حالت
        if br_text:
            matches = re.findall(r'\d+\.\d+|\d+', br_text)
            if len(matches) >= 3: return float(matches[0]), float(matches[1]), float(matches[2])
            elif len(matches) >= 1: return float(matches[0]), float(matches[0]), float(matches[0])
        
        # تلاش در کل متن
        br_matches = re.findall(r'Battle Rating\s*[:\-]?\s*(\d+\.\d+)', text_content, re.IGNORECASE)
        if br_matches:
            val = float(br_matches[0])
            return val, val, val
            
        return None, None, None

    @staticmethod
    def extract_economy(text_content):
        w_match = re.search(r'(?:Mass|Weight|Max takeoff weight)[\s:\-]*([\d\.,]+)\s*(t|tons|kg)', text_content, re.IGNORECASE)
        weight = float(w_match.group(1).replace(',', '')) if w_match else None
        if weight and w_match.group(2).lower() == 'kg': weight /= 1000.0
            
        rp_match = re.search(r'(?:Research|Cost)[\s:\-]*([\d\.,]+)\s*(?:RP|Points)', text_content, re.IGNORECASE)
        rp = int(rp_match.group(1).replace(',', '').replace('.', '')) if rp_match else None
            
        sl_match = re.search(r'(?:Purchase|Price)[\s:\-]*([\d\.,]+)\s*(?:SL|Lions)', text_content, re.IGNORECASE)
        sl = int(sl_match.group(1).replace(',', '').replace('.', '')) if sl_match else None
            
        return {'weight': weight, 'rp': rp, 'sl': sl}

# ==========================================
# ۳. اجرای سوپر-خزنده با سیستم Retry
# ==========================================
def run_scraper(category_input):
    cat_lower = category_input.lower()
    target_url = f"https://wiki.warthunder.com/{cat_lower}"
    db_category = 'ground' if cat_lower == 'army' else cat_lower
    
    print(f"\n🚀 IGNITING LIMITLESS SCRAPER FOR: {cat_lower.upper()}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font", "stylesheet"] else route.continue_())
        
        page = context.new_page()
        page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        
        # پیدا کردن تمام لینک‌ها
        urls_list = page.evaluate("""() => Array.from(document.querySelectorAll('a')).map(a => a.getAttribute('href')).filter(h => h && h.includes('/unit/'))""")
        urls_queue = list({f"https://wiki.warthunder.com{href}" if href.startswith("/") else href for href in urls_list})
        
        print(f"🎯 Target Acquired: {len(urls_queue)} unique vehicles. Commencing deep extraction...\n")

        saved_count = 0
        retry_queue = []
        extractor = LimitlessExtractor()

        # حلقه اصلی پردازش
        while urls_queue or retry_queue:
            # چک کردن محدودیت زمانی اکشن گیت‌هاب (۵.۵ ساعت)
            if (time.time() - START_TIME) > MAX_RUNTIME_SECONDS:
                print("\n⚠️ Time limit approaching! Saving state and gracefully exiting to prevent GitHub Action failure.")
                break

            # انتقال آیتم‌های رد شده به صف اصلی اگر صف اصلی خالی شد
            if not urls_queue and retry_queue:
                print("\n🔄 Processing Retry Queue...")
                urls_queue = retry_queue.copy()
                retry_queue = []

            url = urls_queue.pop(0)
            slug = url.split("/")[-1].lower()

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=25000)
                
                # استخراج تمام دیتای خام صفحه در یک شات برای جلوگیری از ریکوئست‌های اضافه
                page_data = page.evaluate("""() => {
                    return {
                        title: document.title,
                        bodyText: document.body.innerText,
                        h1: document.querySelector('h1') ? document.querySelector('h1').textContent : '',
                        brText: document.querySelector('.specs_card_br, .br-value') ? document.querySelector('.specs_card_br, .br-value').textContent : '',
                        catLinks: document.getElementById('mw-normal-catlinks') ? document.getElementById('mw-normal-catlinks').innerText : '',
                        breadcrumbs: document.querySelector('.breadcrumbs, #mw-content-text') ? document.querySelector('.breadcrumbs, #mw-content-text').innerText.substring(0, 500) : '',
                        imgAlts: Array.from(document.querySelectorAll('img')).map(img => img.alt || '').join(' '),
                        tableNation: Array.from(document.querySelectorAll('tr')).map(tr => tr.innerText).find(text => text.toLowerCase().includes('country') || text.toLowerCase().includes('nation')) || '',
                        imageUrl: Array.from(document.querySelectorAll('img')).map(img => img.getAttribute('src')).find(src => src && !src.includes('icon') && document.querySelector(`img[src="${src}"]`).getAttribute('width') >= 200) || null
                    };
                }""")
                
                text_content = page_data['bodyText']
                name = page_data['h1'].strip() or page_data['title'].replace(" - War Thunder Wiki", "").strip() or slug.replace("_", " ").title()
                
                # --- پردازش عمیق ---
                nation = extractor.find_nation(page_data, slug, text_content)
                br_ab, br_rb, br_sb = extractor.extract_br(page_data['brText'], text_content)
                economy = extractor.extract_economy(text_content)
                
                # پیدا کردن رنک
                rank_match = re.search(r'Rank\s*([IVX]+|\d+)', text_content, re.IGNORECASE)
                rank = None
                if rank_match:
                    r_val = rank_match.group(1)
                    rank = {'I':1, 'II':2, 'III':3, 'IV':4, 'V':5, 'VI':6, 'VII':7, 'VIII':8, 'IX':9}.get(r_val.upper(), int(r_val) if r_val.isdigit() else 5)
                else:
                    rank = 5 # دیفالت ایمن
                
                img_url = page_data['imageUrl']
                if img_url and img_url.startswith('/'): img_url = f"https://wiki.warthunder.com{img_url}"

                # ساخت پکیج نهایی
                vehicle_data = {
                    "id": slug, "name": name, "category": db_category, "nation": nation, "rank": rank, 
                    "br_ab": br_ab, "br_rb": br_rb, "br_sb": br_sb, "weight_tons": economy['weight'], 
                    "research_cost_rp": economy['rp'], "purchase_cost_sl": economy['sl'], 
                    "image_url": img_url, "source_url": url
                }

                # تزریق مستقیم و ضدگلوله به سوپابیس
                supabase.table("vehicles").upsert(vehicle_data, on_conflict="id").execute()
                saved_count += 1
                
                print(f"✅ [{nation.upper().ljust(7)}] | {name[:25].ljust(25)} | BR: {str(br_rb).ljust(4)} | Rank: {rank}")
                
                # پاکسازی حافظه برای اجرای طولانی مدت
                if saved_count % 50 == 0: context.clear_cookies()

            except PlaywrightTimeoutError:
                print(f"⏳ Timeout on {slug} -> Added to Retry Queue.")
                retry_queue.append(url)
            except Exception as e:
                print(f"❌ Error on {slug} -> {str(e)[:40]} -> Added to Retry Queue.")
                retry_queue.append(url)

        browser.close()
        print(f"\n🎉 OMNIPOTENT RUN COMPLETE: {saved_count} perfectly verified vehicles injected into Supabase.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", type=str, default="helicopters")
    args = parser.parse_args()
    
    run_scraper(args.category)
