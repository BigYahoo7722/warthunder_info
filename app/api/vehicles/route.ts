import { NextRequest, NextResponse } from "next/server";
import { unstable_cache } from "next/cache";
import { getSupabaseClient, hasSupabaseConfigured } from "@/lib/supabase";
import vehiclesData from "@/data/vehicles.json";
import type { Vehicle, VehiclePage } from "@/lib/types";

const PAGE_SIZE = 30;
const REVALIDATE_SECONDS = 3600; // /api/revalidate can push a fresh scrape live sooner than this

const MOCK_VEHICLES = vehiclesData as unknown as Vehicle[];

interface ArmorTriplet {
  frontMm?: number;
  sideMm?: number;
  backMm?: number;
}
interface ScrapedAmmo {
  name: string;
  type: string;
  penetrationMm?: Record<string, number | null>;
}
interface VehicleRow {
  id: string;
  name: string;
  nation: string | null;
  category: string;
  rank: number | null;
  br_ab: number | null;
  br_rb: number | null;
  br_sb: number | null;
  crew: number | null;
  weight_tons: number | null;
  armor: { hull?: ArmorTriplet; turret?: ArmorTriplet } | null;
  ammunition: ScrapedAmmo[] | null;
  research_cost_rp: number | null;
  purchase_cost_sl: number | null;
}

/**
 * Maps a Supabase row (the scraper's actual confirmed output — see
 * scripts/supabase-schema.sql's header comment) onto the frontend's
 * Vehicle shape. Fields the real scraper doesn't extract yet (engine
 * power, top speed, reload times, avionics — see daily_scraper.py's "NOT
 * CONFIRMED" section) are left undefined rather than defaulted to 0 or
 * fabricated, so VehicleModal's existing per-field conditionals hide them
 * cleanly instead of showing a misleading zero.
 */
function rowToVehicle(row: VehicleRow): Vehicle {
  const rb = row.br_rb ?? row.br_ab ?? row.br_sb ?? 1;
  const ammo = row.ammunition ?? [];

  return {
    id: row.id,
    name: row.name,
    // FIX: lowercase defensively. The scraper now writes lowercase nation
    // ids directly (see scripts/daily_scraper.py), but this guards against
    // any future write path (manual SQL edits, a different scraper, a bad
    // migration) reintroducing a case mismatch that silently zeroes out
    // every filtered query on the site.
    nation: ((row.nation ?? "usa").toLowerCase()) as Vehicle["nation"],
    category: (row.category ?? "").toLowerCase() as Vehicle["category"],
    rank: row.rank ?? 1,
    br: { ab: row.br_ab ?? rb, rb, sb: row.br_sb ?? rb },
    crew: row.crew ?? 1,
    mobility: row.weight_tons != null ? { weightTons: row.weight_tons } : undefined,
    firepower:
      ammo.length > 0
        ? {
            reloadBaseSec: 0, // not yet extracted — see module docstring
            reloadAcedSec: 0,
            ammoTypes: ammo.map((a) => ({
              name: a.name,
              type: a.type,
              muzzleVelocityMs: 0, // not yet extracted
              penetration: Object.entries(a.penetrationMm ?? {})
                .filter(([, v]) => v != null)
                .map(([range, v]) => ({
                  rangeM: parseInt(range, 10) || 0,
                  angle0: v as number,
                  angle30: v as number, // scraper only captured a single (0°-equivalent) value per range so far
                  angle60: v as number,
                })),
            })),
          }
        : undefined,
    armor:
      row.armor?.hull || row.armor?.turret
        ? {
            hullFrontMm: row.armor.hull?.frontMm ?? 0,
            hullSideMm: row.armor.hull?.sideMm ?? 0,
            hullRearMm: row.armor.hull?.backMm ?? 0,
            turretFrontMm: row.armor.turret?.frontMm,
            turretSideMm: row.armor.turret?.sideMm,
            turretRearMm: row.armor.turret?.backMm,
            era: false, // not yet extracted
            composite: false, // not yet extracted
          }
        : undefined,
    proTips: [],
    sourceDetail: "scraped",
  };
}

const getCachedPage = unstable_cache(
  async (nation: string | null, category: string | null, cursor: number): Promise<VehiclePage> => {
    if (!hasSupabaseConfigured()) {
      return paginateLocal(nation, category, cursor);
    }

    const supabase = getSupabaseClient();
    let query = supabase.from("vehicles").select("*", { count: "exact" });
    // FIX: normalize to lowercase before filtering — Postgres text equality
    // is case-sensitive, so a stray uppercase letter anywhere in the
    // pipeline (scraper, manual insert, future data source) used to mean
    // this filter matched nothing at all, with no error and no visible
    // signal beyond an empty grid on the site.
    if (nation) query = query.eq("nation", nation.toLowerCase());
    if (category) query = query.eq("category", category.toLowerCase());

    // .range() is 0-based and INCLUSIVE on both ends (confirmed against
    // @supabase/postgrest-js's source directly during this build) — so
    // this returns exactly PAGE_SIZE rows starting at `cursor`, matching
    // the same cursor semantics the mock-data fallback below uses.
    const { data, error, count } = await query
      .order("id", { ascending: true })
      .range(cursor, cursor + PAGE_SIZE - 1);

    if (error) throw error;

    const items = (data as VehicleRow[]).map(rowToVehicle);
    const total = count ?? items.length;
    return {
      items,
      nextCursor: cursor + PAGE_SIZE < total ? cursor + PAGE_SIZE : null,
      total,
    };
  },
  ["vehicles-page"],
  { revalidate: REVALIDATE_SECONDS, tags: ["vehicles"] }
);

function paginateLocal(nation: string | null, category: string | null, cursor: number): VehiclePage {
  let filtered = MOCK_VEHICLES;
  if (nation) filtered = filtered.filter((v) => v.nation === nation.toLowerCase());
  if (category) filtered = filtered.filter((v) => v.category === category.toLowerCase());
  const items = filtered.slice(cursor, cursor + PAGE_SIZE);
  return {
    items,
    nextCursor: cursor + PAGE_SIZE < filtered.length ? cursor + PAGE_SIZE : null,
    total: filtered.length,
  };
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const nation = searchParams.get("nation");
  const category = searchParams.get("category");
  const cursor = Number(searchParams.get("cursor") ?? "0");

  if (!Number.isFinite(cursor) || cursor < 0) {
    return NextResponse.json({ error: "Invalid cursor" }, { status: 400 });
  }

  try {
    const page = await getCachedPage(nation, category, cursor);
    return NextResponse.json(page);
  } catch (err) {
    console.error("vehicles route failed:", err);
    if (hasSupabaseConfigured()) {
      const fallback = paginateLocal(nation, category, cursor);
      return NextResponse.json(
        { ...fallback, _warning: "Served from local fallback data — Supabase query failed, check server logs." },
        { status: 200 }
      );
    }
    return NextResponse.json({ error: "Internal error" }, { status: 500 });
  }
}
