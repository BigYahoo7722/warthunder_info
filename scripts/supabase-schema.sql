-- War Thunder Codex — Supabase schema
-- Run this once in Supabase Dashboard -> SQL Editor -> New query -> Run.
--
-- If you already have a `vehicles` table from an earlier version of this
-- project, run scripts/supabase_migration_fix.sql instead — this file's
-- `create table if not exists` will NOT add new columns to an existing
-- table.

create table if not exists vehicles (
  id                text primary key,      -- wiki slug, e.g. "us_m1a2_abrams"
  name              text not null,
  nation            text,                  -- always lowercase, e.g. "usa" — see trigger below
  category          text not null,         -- aviation | army | fleet | helicopters
  rank              integer,
  br_ab             numeric,
  br_rb             numeric,
  br_sb             numeric,
  crew              integer,
  weight_tons       numeric,
  armor             jsonb,                 -- {hull: {frontMm,sideMm,backMm}, turret: {...}}
  ammunition        jsonb,                 -- [{name, type, penetrationMm: {"10m":.., "100m":..,...}}]
  dynamic_specs     jsonb,                 -- raw label->value scrape of the wiki's infobox/specs table
  research_cost_rp  numeric,
  purchase_cost_sl  numeric,
  source_url        text,
  scraped_at        timestamptz,
  updated_at        timestamptz default now()
);

-- The app's primary query pattern is "vehicles for nation X, category Y,
-- ordered, paginated" -- this is exactly what a compound index serves.
create index if not exists idx_vehicles_nation_category on vehicles (nation, category);

-- Keep updated_at current on every upsert, independent of scraped_at
-- (which the scraper sets itself from its own clock).
create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_vehicles_updated_at on vehicles;
create trigger trg_vehicles_updated_at
  before update on vehicles
  for each row execute function set_updated_at();

-- Enforce lowercase nation at the database layer, not just in application
-- code — Postgres text equality is case-sensitive, and the frontend's
-- nation ids (lib/taxonomy.ts) are always lowercase ("usa", "germany",
-- ...). A mismatch here means the site silently shows zero results for a
-- nation with no error anywhere, which is exactly the bug this project
-- shipped with once.
create or replace function enforce_lowercase_nation()
returns trigger as $$
begin
  if new.nation is not null then
    new.nation = lower(new.nation);
  end if;
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_vehicles_lowercase_nation on vehicles;
create trigger trg_vehicles_lowercase_nation
  before insert or update on vehicles
  for each row execute function enforce_lowercase_nation();

-- Row Level Security: the scraper writes with the service_role key, which
-- bypasses RLS entirely and needs no policy. The Next.js app reads with
-- the anon key, which DOES need an explicit policy -- Supabase blocks all
-- access by default once RLS is on. Vehicle stats aren't sensitive, so a
-- plain public-read policy is appropriate; there's deliberately no
-- insert/update/delete policy for anon.
alter table vehicles enable row level security;

drop policy if exists "Public read access" on vehicles;
create policy "Public read access"
  on vehicles for select
  using (true);
