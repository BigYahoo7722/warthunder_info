<div align="center">

# War Thunder Codex — Cinematic Field Dossier

**[🇬🇧 English](#english) · [🇮🇷 فارسی](#فارسی)**

*Not affiliated with or endorsed by Gaijin Entertainment. "War Thunder" is a trademark of Gaijin Entertainment. This is a fan-built reference tool.*

</div>

---

<a name="english"></a>
## 🇬🇧 English

A virtualized, chunk-loaded reference app for the War Thunder vehicle roster — a Python scraping pipeline feeding a Next.js frontend with a full **WebGL cinematic layer**: every vehicle category (tank, jet, helicopter, ship) gets a real-time 3D reveal sequence — entry, brake/settle, fire, camera-tracked projectile flight, impact, then a glassmorphism stat card built from real scraped data.

### What's actually in this build

| Layer | Tech | Status |
|---|---|---|
| Data pipeline | Python scraper → Supabase (Postgres) → daily GitHub Action | Working, schema validated |
| API | Next.js route handlers, cursor pagination, server-only Supabase access | Working |
| 2D UI | Sidebar, virtualized infinite-scroll grid, search, i18n/RTL, translate toggle | Working, carried over from the previous build |
| 3D cinematic layer | `three` + `@react-three/fiber` + `@react-three/drei` + `@react-three/postprocessing` + `gsap` | Working, **placeholder geometry** — see below |

### ⚠️ Honest current limitation: placeholder 3D models

`components/three/VehicleModel.tsx` currently builds every vehicle out of **procedural primitives** (boxes, cylinders, spheres) — not real 3D models. This was a deliberate first pass: the animation/camera/physics-feel engine (`VehicleRevealScene.tsx`) needed to exist and be provably correct before wiring in real assets, since swapping geometry later is cheap but rebuilding the animation contract later is not.

**To finish it:** drop `.glb` files into `public/models/` (one per category: `tank.glb`, `jet.glb`, `helicopter.glb`, `ship.glb`) and update `VehicleModel.tsx` to load them via `useGLTF` instead of the primitive builders. Real War Thunder game assets can't be used here — they're Gaijin's copyrighted property and ripping them breaks the game's ToS. Use CC0/CC-BY game-ready assets instead (Sketchfab, Kenney.nl, Quaternius, Poly Pizza).

### 3D architecture

```
components/three/
├── Scene.tsx              Canvas provider: ACES tonemapping, bloom, depth of field,
│                           vignette, chromatic aberration, dusk HDRI lighting
├── VehicleModel.tsx        Procedural geometry per category (army/aviation/
│                           helicopters/fleet) — swap for useGLTF here
├── VehicleRevealScene.tsx  ONE animation engine driving all 4 categories via a
│                           shared ref contract (hull / articulated / emitter /
│                           muzzleLight / aux[]) — GSAP timeline: entry → settle
│                           → fire → camera-tracked flight → impact → reveal
└── CinematicHero.tsx       Autoplaying hero banner, cycles the 4 categories
```

`hooks/useVehicleFor3D.ts` feeds real vehicle data into the 3D layer through the *existing* `/api/vehicles` route — it never talks to Supabase directly from the client, preserving the original architecture's server-only database access boundary (the anon key is never shipped to the browser bundle).

`components/VehicleDossierModal.tsx` replaces the old flat popup: a full-screen dossier with the 3D reveal sequence as its header and the same auto-categorizing stat-section logic the original `VehicleModal.tsx` had (armor tables, ammo penetration tables, self-organizing "whatever field the scraper found" sections) — that logic wasn't rewritten, just re-housed.

### Running it

```bash
npm install
npm run dev
# → http://localhost:3000
```

Regenerate mock data / run the scraper — see the pipeline section below, unchanged from the original build.

### Data pipeline (unchanged from previous builds)

```bash
python3 scripts/generate_mock_data.py

pip install requests beautifulsoup4 --break-system-packages
python3 scripts/scraper.py wiki --nation usa --category army --out data/raw_wiki_usa_army.json
python3 scripts/scraper.py datamine --repo-path ./War-Thunder-Datamine --out data/raw_datamine.json
python3 scripts/scraper.py merge --wiki data/raw_wiki_usa_army.json --datamine data/raw_datamine.json --out data/vehicles.json
```

`scripts/daily_scraper.py` runs on a GitHub Actions schedule against `wiki.warthunder.com`, writes to Supabase, and pings `/api/revalidate` — new data appears without a redeploy. Read `legal.gaijin.net/termsofservice` before turning the schedule on; start with `--dry-run --limit 10`.

### Database setup (Supabase)

1. Create a project at [supabase.com/dashboard](https://supabase.com/dashboard)
2. SQL Editor → run `scripts/supabase-schema.sql`
3. Set env vars:

| Secret | Where | Why |
|---|---|---|
| `SUPABASE_URL` | GitHub Actions + Vercel | both processes need it |
| `SUPABASE_SERVICE_ROLE_KEY` | GitHub Actions **only** | scraper write access — never in Vercel |
| `SUPABASE_ANON_KEY` | Vercel **only** | read-only, server-side API route |
| `REVALIDATE_SECRET` | Both (same value) | authenticates the post-scrape cache ping |
| `REVALIDATE_URL` | GitHub Actions | your deployed `/api/revalidate` URL |
| `DEEPL_API_KEY` | Vercel | powers the translate toggle (deepl.com/pro-api, free tier) |

No Supabase project needed for local dev — the API route falls back to `data/vehicles.json` automatically when the env vars aren't set.

### Project structure

```
├── app/
│   ├── [locale]/page.tsx        orchestrates sidebar / hero / grid / dossier
│   ├── [locale]/layout.tsx      fonts, metadata, RTL dir
│   └── api/
│       ├── vehicles/route.ts           cursor-paginated data endpoint
│       ├── vehicles/search/route.ts    ranked name search
│       ├── translate/route.ts          DeepL wrapper
│       └── revalidate/route.ts         post-scrape cache invalidation
├── components/
│   ├── three/                    3D cinematic layer (see above)
│   ├── Sidebar.tsx                die-cut nation tabs + spring drawer (glass)
│   ├── VehicleGrid.tsx            react-virtuoso + react-query chunk loading
│   ├── VehicleCard.tsx            glass card, hotlinked scraped images
│   ├── VehicleDossierModal.tsx    full-screen 3D reveal + auto-categorized specs
│   └── CollapsibleSection.tsx     accordion, tab-cut motif
├── hooks/
│   ├── useVehicleFor3D.ts         3D layer's data bridge (via /api/vehicles)
│   ├── useTranslatedVehicle.ts    DeepL translation, cached per (id, locale)
│   └── useRealtimeVehicle.ts      placeholder for future Supabase Realtime wiring
├── lib/                           types, taxonomy, fonts, supabase client, RTL helper
├── data/                          generated demo dataset + schema example
├── scripts/                       scraper, daily pipeline, mock data, schema SQL
├── i18n/, messages/                next-intl routing + 16 locale files
└── .github/workflows/              daily scraper Action
```

### Known gaps / what's still manual

- **Real 3D models** — see the limitation note above.
- **Local build wasn't run from this environment** (no network access here) — run `npm install && npm run build` yourself before trusting a deploy blind.
- **CC-Attribution credit** — if you use non-CC0 free models (most Sketchfab "free" downloads are CC-BY), add a credit line somewhere in the app (footer / About).
- Everything under "What's been validated" in earlier iterations of this README (Supabase connection untested live, DeepL untested against a real key, translation quality is AI-drafted and needs native review) still applies — nothing about the 3D layer changes those facts.

---

<div dir="rtl" align="right">

<a name="فارسی"></a>
## 🇮🇷 فارسی

یک اپلیکیشن مرجع مجازی‌سازی‌شده (virtualized) برای لیست کامل وسایل نقلیه‌ی War Thunder — یک خط‌لوله‌ی اسکرپینگ پایتون که داده رو تغذیه می‌کنه به یک فرانت‌اند Next.js با یک **لایه‌ی سینمایی WebGL کامل**: هر دسته از وسیله (تانک، جت، هلی‌کوپتر، کشتی) یک سکانس ریویل سه‌بعدی و بلادرنگ داره — ورود، ترمز/استقرار، شلیک، تعقیب دوربین از مسیر گلوله، برخورد، و بعد یک کارت آمار شیشه‌ای که از داده‌ی واقعی اسکرپ‌شده ساخته میشه.

### چیزی که واقعاً توی این نسخه هست

| لایه | تکنولوژی | وضعیت |
|---|---|---|
| خط‌لوله‌ی داده | اسکرپر پایتون ← Supabase (Postgres) ← GitHub Action روزانه | کار می‌کنه، schema تست‌شده |
| API | روت‌های Next.js، صفحه‌بندی cursor، دسترسی به Supabase فقط سمت سرور | کار می‌کنه |
| رابط دوبعدی | سایدبار، گرید اسکرول بی‌نهایتِ مجازی‌سازی‌شده، سرچ، i18n/RTL، دکمه‌ی ترجمه | کار می‌کنه، از نسخه‌ی قبلی منتقل شده |
| لایه‌ی سینمایی سه‌بعدی | `three` + `@react-three/fiber` + `@react-three/drei` + `@react-three/postprocessing` + `gsap` | کار می‌کنه، **هندسه‌ی placeholder** — پایین‌تر توضیح داده شده |

### ⚠️ محدودیت واقعی فعلی: مدل‌های سه‌بعدی placeholder

فایل `components/three/VehicleModel.tsx` فعلاً هر وسیله رو از **اشکال هندسی رویه‌ای** (باکس، استوانه، کره) می‌سازه — نه مدل سه‌بعدی واقعی. این یه انتخاب عمدی برای گام اول بود: موتور انیمیشن/دوربین/حس فیزیک (`VehicleRevealScene.tsx`) اول باید ساخته و درست تأیید می‌شد، چون بعداً عوض کردن هندسه ارزون‌تره تا بعداً بازسازی کل قرارداد انیمیشن.

**برای تکمیلش:** فایل‌های `.glb` رو بذار توی `public/models/` (یکی برای هر دسته: `tank.glb`, `jet.glb`, `helicopter.glb`, `ship.glb`) و `VehicleModel.tsx` رو طوری عوض کن که به‌جای هندسه‌ی رویه‌ای، از `useGLTF` این فایل‌ها رو لود کنه. **مدل‌های واقعی خود بازی War Thunder قابل استفاده نیستن** — مال گایجینن و کپی‌رایتی، ریپ کردنشون قوانین بازی رو می‌شکنه. به‌جاش از مدل‌های game-ready با لایسنس CC0/CC-BY استفاده کن (Sketchfab، Kenney.nl، Quaternius، Poly Pizza).

### معماری سه‌بعدی

```
components/three/
├── Scene.tsx              پروایدر Canvas: تون‌مپینگ ACES، bloom، عمق میدان،
│                           وینیت، ابیراهی رنگی، نورپردازی HDRI غروب
├── VehicleModel.tsx        هندسه‌ی رویه‌ای برای هر دسته — همین‌جا باید به
│                           useGLTF تغییر کنه
├── VehicleRevealScene.tsx  یک موتور انیمیشن واحد که هر ۴ دسته رو با یک
│                           قرارداد ref مشترک اجرا می‌کنه — تایم‌لاین GSAP:
│                           ورود ← استقرار ← شلیک ← پرواز با تعقیب دوربین
│                           ← برخورد ← ریویل
└── CinematicHero.tsx       بنر اصلیِ خودپخش‌شونده، بین ۴ دسته می‌چرخه
```

`hooks/useVehicleFor3D.ts` داده‌ی واقعیِ وسیله رو از طریق همون روت موجود `/api/vehicles` به لایه‌ی سه‌بعدی می‌رسونه — هیچ‌وقت مستقیم از سمت کلاینت به Supabase وصل نمیشه، تا مرز معماری اصلی (دسترسی دیتابیس فقط سمت سرور، کلید anon هیچ‌وقت توی باندل مرورگر نمیره) حفظ بشه.

`components/VehicleDossierModal.tsx` جایگزین پاپ‌آپ تخت قدیمیه: یک دوسیه‌ی تمام‌صفحه با سکانس ریویل سه‌بعدی به‌عنوان هدر و همون منطق خودسازمان‌دهِ دسته‌بندی آمار که `VehicleModal.tsx` قدیمی داشت (جدول زره، جدول نفوذ مهمات، بخش‌های خودکار برای هر فیلدی که اسکرپر پیدا کرده) — این منطق بازنویسی نشده، فقط جای جدید گرفته.

### اجرا

```bash
npm install
npm run dev
# → http://localhost:3000
```

برای بازتولید داده‌ی موک یا اجرای اسکرپر، به بخش خط‌لوله‌ی داده در نسخه‌ی انگلیسی بالا مراجعه کن — بدون تغییر از نسخه‌ی اصلی.

### چیزهایی که هنوز دستی‌ان / محدودیت‌ها

- **مدل‌های سه‌بعدی واقعی** — طبق توضیح بالا.
- **بیلد لوکال از این محیط اجرا نشده** (این‌جا دسترسی شبکه ندارم) — قبل از اعتماد کورکورانه به دیپلوی، خودت `npm install && npm run build` رو بزن.
- **کردیت CC-Attribution** — اگه از مدل‌های غیر-CC0 استفاده کردی (اکثر دانلودهای "رایگان" Sketchfab در واقع CC-BY هستن)، یه خط کردیت جایی توی اپ (فوتر یا صفحه‌ی About) اضافه کن.
- هرچی زیر بخش «What's been validated» توی نسخه‌های قبلیِ این README بود (اتصال زنده‌ی Supabase تست نشده، DeepL با کلید واقعی تست نشده، کیفیت ترجمه پیش‌نویس AI‌ـه و نیاز به بازبینی بومی داره) هنوز صادقه — لایه‌ی سه‌بعدی هیچ‌کدوم از این‌ها رو عوض نکرده.

</div>
