# War Thunder Codex — Field Dossier

A virtualized, chunk-loaded reference app for the War Thunder vehicle roster,
plus the Python pipeline meant to feed it real data.

**Not affiliated with or endorsed by Gaijin Entertainment.** "War Thunder" is
a trademark of Gaijin Entertainment. This is a fan-built reference tool, in
the same spirit as the public community projects it's modeled on.

## What's in this build

1. **Frontend** — Next.js 14 (App Router) + TypeScript + Tailwind + Framer
   Motion + React Query + react-virtuoso. Sidebar drawer, hero, virtualized
   infinite-scroll grid, shared-element modal — all wired up and working.
2. **Python scraper** (`scripts/scraper.py`) — MediaWiki-API wiki extractor
   + datamine JSON parser. Tested against real data where noted below.
3. **JSON schema example** (`data/schema-example.json`) — 4 fully-detailed
   top-tier USA/Sweden vehicles, demonstrating every field in the schema.

## Honest scoping decisions

A few places this deliberately doesn't do the literal thing the brief asked
for, and why:

- **"Entire 2,500+ vehicle roster."** Ships with 2,578 vehicles: 7
  hand-authored "flagship" records with full-depth stats, and ~2,570
  procedurally generated placeholder records (`scripts/generate_mock_data.py`).
  Hand-typing 2,500+ real vehicle records isn't something any engineer would
  actually do — that's what the scraper is for. The generated tier exists to
  prove the virtualization/pagination architecture holds up at real roster
  scale. Swap `data/vehicles.json` for the scraper's output when you have it.
- **Hero screenshots.** The brief asks for "high-definition cinematic War
  Thunder screenshots." I can't redistribute Gaijin's copyrighted game
  screenshots, so `components/Hero.tsx` ships with styled gradient /
  redacted-bar placeholder plates instead. Swap in your own captures via the
  `imageUrl` field on `HeroSlide`.
- **"Rigidly locked 60/30 FPS."** No website can literally guarantee a hard
  frame-rate lock — that's a browser/hardware guarantee, not something
  application code can force. What this build does instead, for real:
  virtualizes the DOM (react-virtuoso unmounts off-screen cards), paginates
  the API (only one page's worth of JSON ever transfers), and respects
  `prefers-reduced-motion`. That's the actual lever for keeping a
  2,500-item grid smooth.

## What's been validated, and what hasn't

- **Frontend build** — actually run in the environment that produced this
  project, not just claimed: `npm install` (397 packages), `npx tsc --noEmit`
  (clean, zero errors), and `npm run build` (succeeds — 5/5 static pages
  generated, 159 kB first-load JS for the main route). One real finding from
  running it: Next's built-in font optimizer reaches out for the Google
  Fonts stylesheet even from a plain `<link>` tag, not only from
  `next/font`. In this sandbox that request is blocked by network egress
  rules, so the build prints "Skipped optimizing this font" and continues —
  it doesn't fail the build. In a normal environment with open network
  access, that same step succeeds and the font gets automatically inlined,
  so nothing needs to change for a real deploy; this is just what it looks
  like when that optimization can't reach the network.
- **Datamine parser** — tested end-to-end against the real
  `germ_leopard_2a5.blkx` file from gszabi99/War-Thunder-Datamine (fetched
  live during this build). The first version of the armor extraction was
  wrong: it only read the plain `hull`/`turret` DamageParts groups, which
  turned out to be thin structural backing plates (13–45mm), not the real
  protection. Fixed to scan every armor-bearing group
  (`hull_front_composite_armor`, `turret_ex_special_armor`,
  `heavy_turret_screens`, etc.) after finding the discrepancy by testing
  against the real file — see the comments around `_armor_bearing_groups`
  in `scraper.py` for the full explanation.
- **Wiki extractor** — written against the standard MediaWiki API. Confirmed
  the target (warthunder.fandom.com, CC-BY-SA licensed, ~622 pages) is real
  and MediaWiki-based, but not executed live: this build's sandbox only has
  network access to package registries, not general web hosts. Confirm the
  category names in `NATION_TO_WIKI_CATEGORY` still match before a full run.
- **Official wiki.warthunder.com** — relaunched as a custom "Wiki 3.0" site,
  not MediaWiki. `WikiExtractor.scrape_official_html` is an intentional stub
  rather than a guessed implementation — fill in real selectors after
  inspecting a live page.
- **Aircraft/helicopter datamine parsing** — unverified. Written from the
  repo's folder convention, not a confirmed sample file. Its own output is
  flagged `"_verified": false` for exactly this reason.
- **Crew count from the datamine** — deliberately returns `None`. The real
  Leopard 2A5 file lists 12 separate `machine_gunner_*_dm` zones for a
  4-person crew — those are hit-detection zones, not headcount. Get crew
  count from the wiki pass instead.

## Design language

The brief specified "classified military dossier + bookmark tabs," so
that's the literal design concept here, not just a mood board:

- **Color** — warm near-black (`#0B0C08`), not neutral or blue-black. Brass
  (`#C7A046`) is the one signature accent, used sparingly (stamps, active
  states) rather than glowing everywhere. Muted oxblood (`#8B2A22`) is
  reserved for rare/event tags only. Deliberately not the "near-black +
  bright neon accent" look.
- **Type** — Staatliches (stencil, used sparingly: headlines, vehicle names,
  badges) + IBM Plex Sans (body copy) + IBM Plex Mono (every stat, BR
  number, and status line — a HUD-readout feel). Loaded via a `<link>` tag
  in `app/layout.tsx` rather than `next/font/google` — `next/font/google`
  needs to fetch the font file to build its self-hosted output, so it
  hard-fails with no build-time network access. A `<link>` tag only feeds
  Next's *optional* font-optimization pass, which degrades gracefully
  instead (see "What's been validated" above). `next/font/google` is still
  the better default if your deploy target has open build-time network
  access — switch to it for the self-hosting performance win.
- **Signature motif** — the die-cut folder-tab shape (`.tab-cut` in
  `globals.css`) is used on the sidebar's nation tabs and reused as the
  modal's section dividers, instead of introducing a second decorative
  device for the same job.

## Running it

```bash
npm install
npm run dev
# → http://localhost:3000
```

Regenerate the mock dataset:
```bash
python3 scripts/generate_mock_data.py
```

Run the real scraper (read the ToS/robots.txt note in `scraper.py`'s module
docstring first — it's not optional decoration):
```bash
pip install requests beautifulsoup4 --break-system-packages

python3 scripts/scraper.py wiki --nation usa --category army \
  --out data/raw_wiki_usa_army.json

python3 scripts/scraper.py datamine --repo-path ./War-Thunder-Datamine \
  --out data/raw_datamine.json

python3 scripts/scraper.py merge \
  --wiki data/raw_wiki_usa_army.json \
  --datamine data/raw_datamine.json \
  --out data/vehicles.json
```

## Productionizing

This demo reads `data/vehicles.json` as a flat file, imported straight into
the API route — fine for a few thousand records, but a real deployment
should swap `app/api/vehicles/route.ts`'s data access for an actual
database (Postgres with indexes on `nation`/`category`, or Mongo) once the
scraper is feeding it continuously. The route's contract — nation + category
in, one cursor-bounded page out — doesn't need to change either way.

Other things a real production deploy would add that this build
deliberately left out as out-of-scope for the brief: auth, a CMS/admin UI
for correcting scraped data by hand, image hosting for real screenshots,
and a scheduled job to re-run the pipeline after each game update.

## Project structure

```
war-thunder-codex/
├── app/
│   ├── api/vehicles/route.ts   cursor-paginated data endpoint
│   ├── layout.tsx              fonts, metadata
│   ├── page.tsx                orchestrates sidebar / hero / grid / modal
│   └── globals.css             design tokens, .tab-cut signature shape
├── components/
│   ├── Sidebar.tsx              die-cut nation tabs + spring drawer
│   ├── Hero.tsx                 crossfade + Ken Burns showcase
│   ├── VehicleGrid.tsx          react-virtuoso + react-query chunk loading
│   ├── VehicleCard.tsx          shared layoutId source
│   ├── VehicleModal.tsx         shared layoutId target, full spec sheet
│   └── CollapsibleSection.tsx   accordion, reuses the tab-cut motif
├── lib/
│   ├── types.ts                 canonical Vehicle schema
│   └── taxonomy.ts              nation / category metadata
├── data/
│   ├── vehicles.json             generated demo database (2,578 records)
│   └── schema-example.json       4 full-depth USA/Sweden vehicles
├── scripts/
│   ├── generate_mock_data.py     builds data/vehicles.json
│   ├── flagship_vehicles.py      the 7 hand-authored full-depth records
│   └── scraper.py                the real data pipeline
└── README.md                     this file
```

---

## Update: sidebar fix + i18n/RTL/translation (5-phase brief)

This section covers a second pass: a real sidebar bug fix plus full
internationalization. **This restructures most of `app/`** (locale-based
routing) — if you already pulled the first zip, replace the whole project
rather than patching individual files.

### Phase 1 — sidebar bug, actually fixed

The old hover-based drawer was pinned to `top: 0` regardless of which
nation tab opened it. For a tab near the bottom (Sweden, Israel, China)
the mouse had to travel a long diagonal to reach the drawer, crossing dead
space outside any hoverable element — which fired `mouseleave` and closed
it before the pointer arrived. Fixed by switching to click-to-open /
click-outside-to-close (`pointerdown` listener + ref, Escape-to-close) and
aligning the drawer's position to the clicked tab instead of pinning it to
the top. See `components/Sidebar.tsx`.

### Phase 2 — data architecture

Already satisfied by the first build: the grid and modal already consumed
data via typed props from a React-Query-backed fetch against the API
route, not inline mock data. No rework needed beyond what phases 3-5
touch incidentally.

### Phase 3 + 4 — i18n, RTL, per-locale fonts

- **Library**: `next-intl` v4 — confirmed compatible with Next 14 by
  checking its actual `package.json` peerDependencies in node_modules,
  not assumed.
- **Routing**: `app/[locale]/...`, `middleware.ts`, `i18n/routing.ts`
  (locale list + RTL list in one place), `i18n/navigation.ts`,
  `i18n/request.ts`. API routes stay outside `[locale]` on purpose —
  they're backend endpoints, not localized pages.
- **RTL**: `dir` is set on `<html>` per locale in
  `app/[locale]/layout.tsx`. Most mirroring is free from that alone —
  logical CSS properties (`start-*`/`end-*`, `text-start`, `ms-*`/`me-*`,
  Tailwind's built-in `rtl:` variant) auto-flip under `dir="rtl"`, and a
  plain `flex-row` container reverses visual order automatically. The one
  thing that does NOT auto-flip: Framer Motion's `x` transform, since
  it's a physical pixel offset, not a logical property —
  `lib/direction.ts`'s `useRtlFlip()` exists specifically for that (used
  in the sidebar drawer's slide animation). Numeric values (BR, mm,
  km/h, penetration tables) are wrapped in `<bdi dir="ltr">` throughout
  the modal/card so digits don't get bidi-reordered next to RTL text.
- **Fonts**: `lib/fonts.ts` maps each locale to a display/body/mono role
  triple — Staatliches + IBM Plex Sans + Share Tech Mono for Latin,
  Oswald (confirmed Cyrillic coverage) for Russian display, Vazirmatn for
  Persian/Arabic, Noto Sans SC/JP/KR for CJK, Noto Sans Devanagari for
  Hindi. Loaded via a per-locale `<link>` tag (same build-time-network
  reasoning as the first build), with Tailwind's `font-display`/
  `font-body`/`font-mono` resolving through CSS variables set on `<body>`.

### Phase 5 — translate toggle + `/api/translate`

Sits next to the language switcher in the header, and only appears on a
non-English locale. Translates the *raw data* fields — vehicle name,
pro-tips, armor module notes — through `app/api/translate/route.ts`,
which wraps DeepL. **This needs your own `DEEPL_API_KEY`** — sign up at
deepl.com/pro-api (free tier: 500k characters/month), then:

```bash
# local dev
echo "DEEPL_API_KEY=your-key-here" >> .env.local

# Vercel
vercel env add DEEPL_API_KEY
# or: Project Settings -> Environment Variables in the dashboard
```

Without a key, the toggle still renders but translation requests return a
501 with a clear message — fails visibly, not silently, and the UI falls
back to the original English text with a translate-error note instead of
breaking. Results are cached by React Query per (vehicle id, locale) —
`hooks/useTranslatedVehicle.ts` — so toggling or reopening a vehicle
doesn't re-hit the API or burn quota unnecessarily.

### What's been validated this round

- `npm run build` succeeds — all 21 routes generate (16 locale pages +
  `_not-found` + the 2 API routes).
- Actually inspected the built HTML, not just the exit code: `/fa`
  renders `dir="rtl" lang="fa"` with real Persian text baked into the
  static page; `/en` renders `dir="ltr"` with English. Confirmed via
  `grep` against `.next/server/app/*.html`.
- next-intl's exact API (`getRequestConfig`'s `requestLocale` Promise,
  `defineRouting`, `router.replace(path, {locale})`) was checked against
  the installed package's real type definitions and runtime source
  rather than assumed — this library moves fast enough that guessing
  felt like the wrong call.
- **Translation quality is NOT validated.** See
  `scripts/generate_i18n_messages.py`'s module docstring for the full
  note. Every non-English string is an AI-drafted first pass — get a
  native-speaker review before shipping, especially fa/ar where layout
  and translation risk compound.
- The DeepL integration in `/api/translate` is untested against a real
  key (none available here) — the request/response shape matches DeepL's
  documented API, but confirm with your own key before relying on it.

---

## Update: automated daily pipeline (scraper → Supabase → Next.js, zero redeploys)

Third pass: replaces the static mock JSON with a live pipeline. A Python
scraper runs daily via GitHub Actions, writes to Supabase, and the
Next.js app reads from it with a revalidating cache — new data shows up
without a git push or a Vercel rebuild. (Originally built against
MongoDB, then switched to Supabase on request — see "Database setup"
below for why that's a clean swap and what it touches.)

### On "zero-maintenance, fully autonomous"

Worth saying plainly: no scraper hitting a live website is ever truly
zero-maintenance. Sites change their markup, and a selector that's correct
today can silently start returning nothing in six months. What this
pipeline actually delivers is close to that in practice, with one honest
difference — it **fails loudly instead of failing silently**:

- `daily_scraper.py` exits non-zero if more than 15% of vehicles fail to
  scrape in a run, which shows up as a red GitHub Actions run (and an
  email, if you have workflow-failure notifications on) rather than
  quietly writing a half-empty roster.
- The Next.js side always has a fallback (`data/vehicles.json`) — if
  Supabase is unreachable, the API route serves the last-known mock/seed
  data with a `_warning` field instead of a hard 500.

That's the real, achievable version of "hands-off": it runs unattended
right up until the day the site changes, and that day is visible to you
immediately instead of discovered a month later when someone notices the
data looks stale.

### Grounding this scraper actually happened, not assumed

`daily_scraper.py` targets `wiki.warthunder.com` (the OFFICIAL site,
different from the CC-BY-SA Fandom mirror the original `scraper.py`
used). Before writing a line of it, I fetched two real, live pages —
`/unit/us_m1a2_abrams` and the `/ground` category listing — and confirmed:

- The URL pattern (`/unit/{slug}`) and that category pages
  (`/aviation`, `/helicopters`, `/ground`, `/ships`, `/boats`) each embed
  a full tech tree with a plain link per vehicle — no pagination needed
  for discovery.
- Real field labels ("Rank", "Crew", armor as "Hull 133 / 60 / 32 mm",
  etc.) and a genuine HTML `<table>` for ammunition penetration data.
- A real problem: multi-mode stats (forward/backward speed, engine power,
  turret rotation) render **concatenated with no separator** in the
  text-flattened view available to this build (e.g. "Forward 6876 km/h"
  for what's almost certainly 4 stacked per-mode values). Rather than
  guess a split point and ship wrong numbers with false confidence, those
  fields are simply not extracted yet — see the module docstring's "NOT
  CONFIRMED" section for exactly what to check once you can open browser
  devtools on the live page.

This is genuinely different from `daily_scraper.py`'s exact CSS
selectors, which I could NOT verify this way — I only ever had a
text-rendered view of these pages, never the raw DOM. The label-based
`text_after_label()` locator strategy is a deliberate hedge against that
(more resilient to a pure styling refactor than a guessed class name
would be), not a substitute for a real live-browser check before trusting
it against the full roster.

### Read this before turning the schedule on

`wiki.warthunder.com` is Gaijin's own first-party site, not a community
mirror — daily automated crawling is a more sustained activity than a
one-off fetch. Read https://legal.gaijin.net/termsofservice first. Start
with `python3 scripts/daily_scraper.py --category army --limit 10
--dry-run` (no database needed) to sanity-check the extraction before
pointing it at the full roster on a schedule.

### Database setup (Supabase, free tier)

Switched from the originally-planned MongoDB to Supabase (Postgres) on
request. The nested `Vehicle` shape now lives as a mix of scalar columns
(for the fields the app filters/sorts on) plus `jsonb` columns for the
armor/ammunition sub-objects — see `scripts/supabase-schema.sql`'s header
comment for why the schema matches the scraper's actual confirmed output
rather than the full frontend type (some fields — engine power, top
speed, reload times, avionics — aren't extracted yet; see
`daily_scraper.py`'s "NOT CONFIRMED" section).

1. **Create a project**: [supabase.com/dashboard](https://supabase.com/dashboard) → New project → pick a name/region/password (save the password, you won't see it again).
2. **Run the schema**: Dashboard → SQL Editor → New query → paste the full contents of `scripts/supabase-schema.sql` → Run. This creates the `vehicles` table, its index, and the RLS read policy in one go.
3. **Get your keys**: Dashboard → Project Settings → API. You need two different keys for two different roles — this distinction matters, don't mix them up:
   - **`service_role` key** — secret, full read/write, bypasses RLS. Only for the scraper.
   - **`anon` key** — public-safe, read-only (enforced by the RLS policy from step 2). For the Next.js app.
4. **Project URL**: same page as the keys, looks like `https://xxxxxxxx.supabase.co`.

### Where each secret goes

The scraper (GitHub Actions) and the live site (Vercel) are two different
processes using two different keys against the same project:

| Secret | Value | Where | Why |
|---|---|---|---|
| `SUPABASE_URL` | Project URL | GitHub Actions secrets **and** Vercel env vars | both processes need it |
| `SUPABASE_SERVICE_ROLE_KEY` | `service_role` key | GitHub Actions secrets **only** | so `daily_scraper.py` can write — never put this in Vercel or anywhere client-reachable |
| `SUPABASE_ANON_KEY` | `anon` key | Vercel env vars **only** | so `app/api/vehicles` can read |
| `REVALIDATE_SECRET` | any strong random string you choose | Both (same value in each) | authenticates the post-scrape cache-invalidation ping |
| `REVALIDATE_URL` | your deployed site + `/api/revalidate` | GitHub Actions secrets only | e.g. `https://your-app.vercel.app/api/revalidate` |

### Local development

No Supabase project needed for local dev — `app/api/vehicles/route.ts`
checks `hasSupabaseConfigured()` and falls back to `data/vehicles.json`
automatically when `SUPABASE_URL`/`SUPABASE_ANON_KEY` aren't set.
Confirmed by actually starting the built app and curling the route in
this environment (no Supabase project reachable here either): real 200
response, real paginated JSON, `nextCursor` correct — same check repeated
repeated here after switching from the originally MongoDB-backed version,
not assumed to still work just because the Mongo version did.

### A finding worth flagging: `npm audit`

`npm audit` reports several high-severity advisories against Next.js
14.2.35 — which is the *latest available* 14.2.x patch, so these haven't
been backported to the 14.x line; several relate to Server Actions,
`next/image` remote patterns, and custom servers, none of which this
project uses, but a few (middleware bypass, rewrite request smuggling)
are more general. I didn't attempt a Next 15 upgrade in this pass — that's
a bigger, riskier change (async `params`, among other breaking changes)
that deserves its own dedicated, tested pass rather than a rushed
end-of-task jump. Recommendation: budget time for a proper Next 15
migration; `next-intl` v4 (already in use here) supports it.

### What's been validated this round

- `npx tsc --noEmit` — clean.
- `npm run build` — succeeds, same 16 locale pages + 3 API routes as
  before, Supabase-aware route compiles without a live database available.
- **Actually started the built app and hit the live endpoint** — not just
  a build-success claim: `curl localhost:4402/api/vehicles?nation=usa&category=army`
  returned HTTP 200 with real paginated JSON (30 items, `total: 56`,
  correct `nextCursor`), confirming the Supabase→local-fallback path works
  at runtime, not just in the type system.
- `unstable_cache`'s per-argument cache-key behavior — checked directly
  against Next's installed source
  (`node_modules/next/dist/server/web/spec-extension/unstable-cache.js`)
  rather than assumed: runtime arguments ARE combined with `keyParts` to
  form the cache key, confirming different (nation, category, cursor)
  combinations get independent cache entries and revalidation clocks.
- **NOT validated**: any actual Supabase connection (no real project
  available in this environment), the scraper against the live wiki with
  a real browser (Playwright wasn't executed here — see the "NOT
  CONFIRMED" section in `daily_scraper.py`'s docstring), and the GitHub
  Actions workflow itself (no way to trigger a real Actions run from here).
