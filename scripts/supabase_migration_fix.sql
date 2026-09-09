-- War Thunder Codex — migration fix for an EXISTING `vehicles` table
-- Run this instead of supabase-schema.sql if you already have a `vehicles`
-- table from an earlier version of this project — `create table if not
-- exists` in supabase-schema.sql does NOT add new columns to a table that
-- already exists, so a table created before a given column was added to
-- this project would silently be missing it forever otherwise.
--
-- FIX: supabase-schema.sql's own header comment has referenced this exact
-- filename since the very first version of this project, but the file
-- itself was never actually created — anyone who hit the "I already have
-- a vehicles table" case had nothing to run. This is that file, now.
--
-- Safe to run multiple times (every ADD COLUMN uses IF NOT EXISTS).

alter table vehicles add column if not exists image_url text;
alter table vehicles add column if not exists dynamic_specs jsonb;
alter table vehicles add column if not exists research_cost_rp numeric;
alter table vehicles add column if not exists purchase_cost_sl numeric;

-- Re-run these unconditionally — CREATE OR REPLACE / DROP IF EXISTS make
-- them safe even if the table already had the trigger/index from an
-- earlier run of supabase-schema.sql.
create index if not exists idx_vehicles_nation_category on vehicles (nation, category);

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

alter table vehicles enable row level security;

drop policy if exists "Public read access" on vehicles;
create policy "Public read access"
  on vehicles for select
  using (true);
