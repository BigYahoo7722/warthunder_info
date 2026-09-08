"use client";

import { useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Sidebar } from "@/components/Sidebar";
import CinematicHero from "@/components/three/CinematicHero";
import { VehicleGrid } from "@/components/VehicleGrid";
import { VehicleDossierModal } from "@/components/VehicleDossierModal";
import { VehicleSearch } from "@/components/VehicleSearch";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { TranslateToggle } from "@/components/TranslateToggle";
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
  const t = useTranslations();
  const [selection, setSelection] = useState<{
    nation: Nation;
    category: Category;
  } | null>(null);
  const [openVehicle, setOpenVehicle] = useState<Vehicle | null>(null);
  const [translateEnabled, setTranslateEnabled] = useState(false);
  // The real scrollable region is this <main> element (see its
  // "overflow-y-auto" below), not the browser window — the app shell is
  // pinned to h-screen with overflow-hidden above it. VehicleGrid tracks
  // this ref directly so its infinite-scroll fires on the real container.
  const scrollParentRef = useRef<HTMLElement>(null);

  return (
    <QueryClientProvider client={queryClient}>
      {/* Ambient cinematic backdrop for every screen that ISN'T actively
          running its own <Canvas> (hero / dossier reveal) — keeps the mood
          continuous without paying for a second live WebGL context. */}
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 -z-10 bg-ink"
        style={{
          backgroundImage:
            "radial-gradient(ellipse 80% 50% at 20% -10%, rgba(199,160,70,0.10), transparent 60%), radial-gradient(ellipse 60% 40% at 90% 110%, rgba(90,140,255,0.06), transparent 60%)",
        }}
      />

      <div className="flex h-screen flex-col">
        <header className="flex shrink-0 items-center justify-between border-b border-hairline/70 bg-panel/50 px-4 py-2.5 backdrop-blur-md">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 shrink-0 rounded-full bg-brass" />
            <p className="font-mono text-[11px] uppercase tracking-widest2 text-parchment/60">
              {t("header.classified")}
            </p>
          </div>
          <div className="flex items-center gap-4">
            {selection && (
              <button
                type="button"
                onClick={() => setSelection(null)}
                className="flex items-center gap-1.5 font-mono text-[11px] uppercase tracking-widest2 text-parchment/50 transition-colors hover:text-brass"
              >
                <span aria-hidden className="inline-block rtl:rotate-180">←</span>
                {t("header.cover")}
              </button>
            )}
            <TranslateToggle enabled={translateEnabled} onChange={setTranslateEnabled} />
            <LanguageSwitcher />
          </div>
        </header>

        <div className="flex flex-1 overflow-hidden">
          <Sidebar
            activeSelection={selection}
            onSelect={(nation, category) => setSelection({ nation, category })}
          />
          <main ref={scrollParentRef} className="flex-1 overflow-y-auto">
            <CinematicHero visible={!selection} />
            {!selection && (
              <div className="py-2">
                <VehicleSearch onSelect={(nation, category) => setSelection({ nation, category })} />
              </div>
            )}
            {selection && (
              <VehicleGrid
                nation={selection.nation}
                category={selection.category}
                onOpenVehicle={setOpenVehicle}
                scrollParentRef={scrollParentRef}
              />
            )}
            {!selection && (
              <div className="p-10 text-center">
                <p className="font-mono text-xs uppercase tracking-widest2 text-parchment/40">
                  {t("sidebar.selectPrompt")}
                </p>
              </div>
            )}
          </main>
        </div>
      </div>

      <VehicleDossierModal
        vehicle={openVehicle}
        onClose={() => setOpenVehicle(null)}
        translateEnabled={translateEnabled}
      />
    </QueryClientProvider>
  );
}
