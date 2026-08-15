import { NextRequest, NextResponse } from "next/server";
import vehiclesData from "@/data/vehicles.json";
import type { Vehicle, VehiclePage, Category, Nation } from "@/lib/types";

const PAGE_SIZE = 30;

// In-memory "database." A real deployment swaps this module for a query
// against Postgres/Mongo/etc. — see README "Productionizing" — but the
// route's contract (nation + category in, one cursor-bounded page out)
// doesn't change either way.
const ALL_VEHICLES = vehiclesData as unknown as Vehicle[];

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const nation = searchParams.get("nation") as Nation | null;
  const category = searchParams.get("category") as Category | null;
  const cursor = Number(searchParams.get("cursor") ?? "0");

  if (!Number.isFinite(cursor) || cursor < 0) {
    return NextResponse.json({ error: "Invalid cursor" }, { status: 400 });
  }

  let filtered = ALL_VEHICLES;
  if (nation) filtered = filtered.filter((v) => v.nation === nation);
  if (category) filtered = filtered.filter((v) => v.category === category);

  const items = filtered.slice(cursor, cursor + PAGE_SIZE);
  const nextCursor =
    cursor + PAGE_SIZE < filtered.length ? cursor + PAGE_SIZE : null;

  const page: VehiclePage = { items, nextCursor, total: filtered.length };

  // Small artificial delay so the "pulling next chunk" state is visible in
  // the demo instead of resolving instantly from an in-memory array. Remove
  // once this is backed by a real database with its own real latency.
  await new Promise((r) => setTimeout(r, 120));

  return NextResponse.json(page);
}
