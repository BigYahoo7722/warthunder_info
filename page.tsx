"use client";

import { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Sidebar } from "@/components/Sidebar";
import { Hero } from "@/components/Hero";
import { VehicleGrid } from "@/components/VehicleGrid";
import { VehicleModal } from "@/components/VehicleModal";
import type { Category, Nation, Vehicle } from "@/lib/types";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
    },
  },
});

export default function Home() {
  const [selection, setSelection] = useState<{
    nation: Nation;
    category: Category;
  } | null>(null);
  const [openVehicle, setOpenVehicle] = useState<Vehicle | null>(null);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex h-screen flex-col">
        <header className="flex shrink-0 items-center justify-between border-b border-hairline bg-panel px-4 py-2.5">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-brass" />
            <p className="font-mono text-[11px] uppercase tracking-widest2 text-parchment/60">
              Classified — War Thunder Codex
            </p>
          </div>
          {selection && (
            <button
              type="button"
              onClick={() => setSelection(null)}
              className="font-mono text-[11px] uppercase tracking-widest2 text-parchment/50 transition-colors hover:text-brass"
            >
              ← Cover
            </button>
          )}
        </header>

        <div className="flex flex-1 overflow-hidden">
          <Sidebar
            activeSelection={selection}
            onSelect={(nation, category) => setSelection({ nation, category })}
          />
          <main className="flex-1 overflow-y-auto">
            <Hero visible={!selection} />
            {selection && (
              <VehicleGrid
                nation={selection.nation}
                category={selection.category}
                onOpenVehicle={setOpenVehicle}
              />
            )}
            {!selection && (
              <div className="p-10 text-center">
                <p className="font-mono text-xs uppercase tracking-widest2 text-parchment/40">
                  Select a nation on the left to open its file.
                </p>
              </div>
            )}
          </main>
        </div>
      </div>

      <VehicleModal vehicle={openVehicle} onClose={() => setOpenVehicle(null)} />
    </QueryClientProvider>
  );
}
