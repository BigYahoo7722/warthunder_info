"use client";

import { useQuery } from "@tanstack/react-query";
import type { Vehicle, VehiclePage, Category, Nation } from "@/lib/types";

/**
 * Bridges the 3D cinematic components to the SAME data path the rest of
 * the app already uses: the client calls /api/vehicles, and that route
 * (server-side only) talks to Supabase or falls back to data/vehicles.json.
 *
 * Deliberately NOT calling Supabase directly from this hook — this file
 * runs in the browser ("use client"), and lib/supabase.ts's client is
 * server-only by design (see its own comments: SUPABASE_ANON_KEY is never
 * exposed to the client bundle, every Supabase call happens inside an
 * app/api/* route). Going through /api/vehicles keeps that boundary
 * intact instead of quietly punching a hole in it.
 */
async function fetchVehiclePage(nation: Nation | null, category: Category | null, cursor: number): Promise<VehiclePage> {
  const params = new URLSearchParams({ cursor: String(cursor) });
  if (nation) params.set("nation", nation);
  if (category) params.set("category", category);
  const res = await fetch(`/api/vehicles?${params.toString()}`);
  if (!res.ok) throw new Error(`vehicles request failed: ${res.status}`);
  return res.json();
}

/**
 * Picks a vehicle to drive a category's hero/reveal sequence. Prefers a
 * squadron/flagship vehicle if the current page happens to include one,
 * otherwise just uses the first real result for that category — either
 * way it's a genuine row from Supabase/vehicles.json, never invented.
 */
export function useFlagshipFor3D(category: Category) {
  return useQuery<Vehicle | null>({
    queryKey: ["flagship-3d", category],
    queryFn: async () => {
      const page = await fetchVehiclePage(null, category, 0);
      if (page.items.length === 0) return null;
      return page.items.find((v) => v.isSquadron) ?? page.items[0];
    },
    staleTime: 10 * 60 * 1000,
  });
}

/**
 * Looks up one vehicle by id for the 3D layer. /api/vehicles doesn't
 * expose a single-id endpoint yet, so this walks pages of its own
 * category/nation-scoped results — fine for the small pages this app
 * already paginates in (PAGE_SIZE = 30 server-side).
 */
export function useVehicleFor3D(vehicleId: string, hint?: { nation?: Nation; category?: Category }) {
  return useQuery<Vehicle | null>({
    queryKey: ["vehicle-3d", vehicleId, hint?.nation, hint?.category],
    queryFn: async () => {
      let cursor = 0;
      for (let i = 0; i < 20; i++) { // hard cap so a bad id can't loop forever
        const page = await fetchVehiclePage(hint?.nation ?? null, hint?.category ?? null, cursor);
        const found = page.items.find((v) => v.id === vehicleId);
        if (found) return found;
        if (page.nextCursor == null) break;
        cursor = page.nextCursor;
      }
      return null;
    },
    staleTime: 5 * 60 * 1000,
  });
}
