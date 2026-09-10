۶ فایلی که کم بودن + یه فایل که باگش فیکس شد:

آپلود کن (Add file → Upload files) توی مسیرهای دقیقاً همینی که این پوشه نشون میده:

.github/workflows/scraper-aviation.yml     ← جدید (اسکرپر جمعه/شنبه - جت)
.github/workflows/scraper-fleet.yml        ← جدید (اسکرپر سه‌شنبه - کشتی)
.github/workflows/scraper-ground.yml       ← جدید (اسکرپر یکشنبه - تانک)
.github/workflows/scraper-helicopter.yml   ← جدید (اسکرپر دوشنبه - هلی‌کوپتر)
.gitignore                                  ← جدید (روت ریپو)
app/api/revalidate/route.ts                 ← جایگزین (کامنت باگ‌دارش فیکس شد)

بعد از آپلود، این ۱۳ فایل .gitkeep که برای ساخت پوشه‌ها استفاده کردیم
رو پاک کن (دیگه لازم نیستن، کارشون تموم شده):

app/[locale]/.gitkeep
app/api/vehicles/.gitkeep
app/api/vehicles/search/.gitkeep
app/api/translate/.gitkeep
app/api/revalidate/.gitkeep
components/.gitkeep
components/three/.gitkeep
hooks/.gitkeep
lib/.gitkeep
data/.gitkeep
scripts/.gitkeep
i18n/.gitkeep
messages/.gitkeep
.github/workflows/.gitkeep

بعد از این کار:
  git add .
  git commit -m "add daily scraper workflows"
  git push

مهم: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, REVALIDATE_SECRET,
REVALIDATE_URL باید توی GitHub repo Settings → Secrets and variables →
Actions ست شده باشن، وگرنه این workflow ها موقع اجرا فیل میشن. اینا
از قبل اگه نداری، باید بسازیشون (README بخش "Where each secret goes"
رو ببین).
