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
