# در داخل حلقه while urls_queue or retry_queue و درون بلاک try:

page_data = page.evaluate("""() => {
    // گرفتن تمام ردیف‌های جدول مشخصات
    const infoRows = Array.from(document.querySelectorAll('.infobox tr, .specs-card tr'));
    
    // ساخت یک آبجکت کاملا داینامیک از تمام ویژگی‌های هلیکوپتر
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
        bodyText: document.body.innerText,
        h1: document.querySelector('h1') ? document.querySelector('h1').textContent : '',
        catLinks: document.getElementById('mw-normal-catlinks') ? document.getElementById('mw-normal-catlinks').innerText : '',
        imageUrl: Array.from(document.querySelectorAll('img')).map(img => img.getAttribute('src')).find(src => src && !src.includes('icon') && document.querySelector(`img[src="${src}"]`).getAttribute('width') >= 200) || null,
        dynamicData: dynamicData // <--- قلب ارگانیسم
    };
}""")

text_content = page_data['bodyText']
raw_name = page_data['h1'].strip() or page_data['title'].strip()
clean_name = re.sub(r'[\-\|]?\s*War Thunder.*$', '', raw_name, flags=re.IGNORECASE).strip()
if not clean_name: clean_name = slug.replace("_", " ").title()
nation = extractor.find_nation(page_data, slug, text_content)

# جدا کردن اطلاعات کلیدی برای سئو و فیلتر کردن
core_stats = {
    "br": page_data['dynamicData'].get('battle_rating', None),
    "rank": page_data['dynamicData'].get('rank', 'V')
}

img_url = page_data['imageUrl']
if img_url and img_url.startswith('/'): img_url = f"https://wiki.warthunder.com{img_url}"

# ساخت پکیج ارگانیک
organic_payload = {
    "id": slug,
    "name": clean_name,
    "nation": nation,
    "category": db_category,
    "core_stats": core_stats,
    "dynamic_specs": page_data['dynamicData'] # هرچیزی که پیدا کرده اینجا قرار میگیره!
}

try:
    # تزریق به رگ‌های سوپابیس
    supabase.table("living_vehicles").upsert(organic_payload, on_conflict="id").execute()
    saved_count += 1
    print(f"🧬 Evolved: {clean_name[:25].ljust(25)} | Specs Count: {len(page_data['dynamicData'])}")
except Exception as db_err:
    print(f"⚠️ Evolution Blocked on {slug}: {str(db_err)[:80]}")
