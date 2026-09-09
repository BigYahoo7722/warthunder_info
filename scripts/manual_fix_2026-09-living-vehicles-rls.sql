-- ============================================================
-- چک دیتابیس واقعی (project etdxvryhsvcrfhugaibw) — چیزی که پیدا شد
-- ============================================================

-- ۱) مشکل امنیتیِ جدی: جدول living_vehicles اصلاً RLS نداره
-- یعنی هر کسی با anon key (همون کلید عمومی که توی مرورگر می‌ره) می‌تونه
-- بدون هیچ محدودیتی این جدول رو بخونه/بنویسه/پاک کنه.
-- این جدول توی کل کدبیس صفر بار استفاده شده (grep زدم، هیچ فایلی
-- بهش رفرنس نمی‌ده) و صفر ردیف داره — به‌نظر می‌رسه یا باقی‌مونده‌ی یه
-- فیچر ناتموم قدیمیه یا اشتباهی ساخته شده.
--
-- گزینه A — نگه‌دار ولی امن کن (اگه قراره بعداً ازش استفاده کنی):
alter table living_vehicles enable row level security;
create policy "Public read access" on living_vehicles for select using (true);

-- گزینه B — پاکش کن (اگه مطمئنی لازمش نداری):
-- drop table if exists living_vehicles;

-- فقط یکی از این دو تا رو اجرا کن، نه هر دو.


-- ============================================================
-- ۲) پاکسازی اختیاری: ۷ ستون یتیم روی جدول vehicles
-- ============================================================
-- این ستون‌ها (type, battle_rating, max_speed, engine_power, weight,
-- purchase_cost_ge, description) روی جدول واقعی هستن ولی:
--   - scripts/daily_scraper.py هیچ‌وقت روشون نمی‌نویسه (چک کردم upsert
--     رو، فقط ۱۷ ستون مشخص می‌نویسه که هیچ‌کدوم این‌ها نیست)
--   - app/api/vehicles/route.ts هم هیچ‌وقت نمی‌خونتشون
-- یعنی به احتمال زیاد از یه نسخه‌ی قدیمی‌تر (احتمالاً همون نسخه‌ی
-- MongoDB که REAME می‌گه قبلاً بوده) روی جدول موندن. خطرناک نیستن،
-- فقط فضای اضافی مصرف می‌کنن. اختیاریه، اگه مطمئن نیستی دست نزن:

-- alter table vehicles drop column if exists type;
-- alter table vehicles drop column if exists battle_rating;
-- alter table vehicles drop column if exists max_speed;
-- alter table vehicles drop column if exists engine_power;
-- alter table vehicles drop column if exists weight;
-- alter table vehicles drop column if exists purchase_cost_ge;
-- alter table vehicles drop column if exists description;
