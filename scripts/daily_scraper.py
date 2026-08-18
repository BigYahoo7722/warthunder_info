import re

# ۱. استخراج کشور با ۴ لایه لایه‌بندی امنیتی
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

    # لایه ۱: بررسی عکس پرچم یا متن موجود در Infobox
    try:
        flag_imgs = page.locator(".specs_card_nation img, .general_info_nation img").all()
        for img in flag_imgs:
            alt_text = (img.get_attribute("alt") or "").lower()
            src_text = (img.get_attribute("src") or "").lower()
            for key, val in nation_map.items():
                if key in alt_text or key in src_text:
                    return val
    except Exception:
        pass

    # لایه ۲: بررسی دسته‌بندی‌های انتهای صفحه (Categories)
    try:
        categories = [cat.lower() for cat in page.locator("#mw-normal-catlinks a").all_inner_texts()]
        for cat in categories:
            for key, val in nation_map.items():
                if key in cat:
                    return val
    except Exception:
        pass

    # لایه ۳: بررسی آدرس صفحه (URL)
    try:
        url = page.url.lower()
        for key, val in nation_map.items():
            if f"_{key}" in url or f"/{key}" in url:
                return val
    except Exception:
        pass

    return None


# ۲. استخراج رنک (Rank) و تبدیل اعداد رومی (I-VIII) به عدد صحیح
def extract_rank(page):
    roman_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8}
    
    try:
        # لایه ۱: خواندن از المان مشخصات اصلی
        rank_text = page.locator(".specs_card_rank, .general_info_rank").inner_text().strip()
        match = re.search(r'Rank\s+([I|V|X]+|\d+)', rank_text, re.IGNORECASE)
        if match:
            val = match.group(1).upper()
            return roman_map.get(val, int(val) if val.isdigit() else None)
    except Exception:
        pass

    try:
        # لایه ۲: جستجو در دسته‌بندی‌های انتهای صفحه
        categories = page.locator("#mw-normal-catlinks a").all_inner_texts()
        for cat in categories:
            match = re.search(r'Rank\s+([I|V|X]+|\d+)', cat, re.IGNORECASE)
            if match:
                val = match.group(1).upper()
                return roman_map.get(val, int(val) if val.isdigit() else None)
    except Exception:
        pass

    return None


# ۳. استخراج وزن، RP و SL با Regex قدرتمند
def extract_specs_extra(page):
    text_content = ""
    try:
        text_content = page.locator(".mw-parser-output").inner_text()
    except Exception:
        pass

    # استخراج وزن (Weight)
    weight = None
    weight_match = re.search(r'Mass|Weight[:\s]+([\d\.,]+)\s*(t|tons|kg)', text_content, re.IGNORECASE)
    if weight_match:
        try:
            val = float(weight_match.group(1).replace(',', ''))
            weight = val if weight_match.group(2).lower() != 'kg' else val / 1000.0
        except ValueError:
            pass

    # استخراج هزینه تحقیق (RP)
    rp = None
    rp_match = re.search(r'([\d\s,]+)\s*(?:RP|Research Points)', text_content)
    if rp_match:
        try:
            rp = int(rp_match.group(1).replace(',', '').replace(' ', ''))
        except ValueError:
            pass

    # استخراج هزینه خرید (SL)
    sl = None
    sl_match = re.search(r'([\d\s,]+)\s*(?:Silver Lions|SL)', text_content)
    if sl_match:
        try:
            sl = int(sl_match.group(1).replace(',', '').replace(' ', ''))
        except ValueError:
            pass

    return weight, rp, sl
