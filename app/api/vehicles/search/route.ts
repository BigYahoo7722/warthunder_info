import { NextRequest, NextResponse } from "next/server";
import { getSupabaseClient, hasSupabaseConfigured } from "@/lib/supabase";
import vehiclesData from "@/data/vehicles.json";
import type { Vehicle } from "@/lib/types";

const MOCK_VEHICLES = vehiclesData as unknown as Vehicle[];
const MAX_RESULTS = 8;

export interface SearchResult {
  id: string;
  name: string;
  nation: string;
  category: string;
  rank: number | null;
}

/**
 * Ranks matches so the search narrows the way a person expects while
 * typing: exact match first, then "starts with" (typing "a" surfaces
 * names beginning with A before anything else), then a match on a whole
 * word inside the name ("mig 15" matching "Bf 109 mig-swap" style
 * mid-name hits), then any other substring match as a last resort. Within
 * the same rank, shorter names sort first — as the query gets more
 * complete, the closest/shortest matching name should be the one on top.
 */
function matchRank(name: string, query: string): number {
  const n = name.toLowerCase();
  const q = query.toLowerCase();
  if (n === q) return 0;
  if (n.startsWith(q)) return 1;
  if (n.includes(` ${q}`)) return 2;
  return 3;
}

function rankAndTrim(items: SearchResult[], query: string): SearchResult[] {
  return items
    .filter((v) => v.name.toLowerCase().includes(query.toLowerCase()))
    .sort((a, b) => {
      const ra = matchRank(a.name, query);
      const rb = matchRank(b.name, query);
      if (ra !== rb) return ra - rb;
      return a.name.length - b.name.length;
    })
    .slice(0, MAX_RESULTS);
}

export async function GET(req: NextRequest) {
  const q = (req.nextUrl.searchParams.get("q") ?? "").trim();
  if (q.length < 1) {
    return NextResponse.json({ items: [] as SearchResult[] });
  }

  if (!hasSupabaseConfigured()) {
    const items = rankAndTrim(
      MOCK_VEHICLES.map((v) => ({
        id: v.id,
        name: v.name,
        nation: v.nation,
        category: v.category,
        rank: v.rank,
      })),
      q
    );
    return NextResponse.json({ items });
  }

  try {
    const supabase = getSupabaseClient();
    // Over-fetch a bit (30) so client-side ranking has enough candidates
    // to pick the best MAX_RESULTS from, since Postgres's ilike alone
    // doesn't know about "starts with" vs "contains" priority.
    const { data, error } = await supabase
      .from("vehicles")
      .select("id,name,nation,category,rank")
      .ilike("name", `%${q}%`)
      .limit(30);

    if (error) throw error;

    const items = rankAndTrim((data ?? []) as SearchResult[], q);
    return NextResponse.json({ items });
  } catch (err) {
    console.error("vehicle search failed:", err);
    // Fall back to local data rather than a hard error — a broken search
    // box shouldn't be a worse experience than a slightly-stale one.
    const items = rankAndTrim(
      MOCK_VEHICLES.map((v) => ({
        id: v.id,
        name: v.name,
        nation: v.nation,
        category: v.category,
        rank: v.rank,
      })),
      q
    );
    return NextResponse.json({ items, _warning: "Served from local fallback data." });
  }
}
