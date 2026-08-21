"use client";

import { useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Sidebar } from "@/components/Sidebar";
import { Hero } from "@/components/Hero";
import { VehicleGrid } from "@/components/VehicleGrid";
import { VehicleModal } from "@/components/VehicleModal";
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
  // FIX: the real scrollable region is this <main> element (see its
  // "overflow-y-auto" below), not the browser window — the app shell is
  // pinned to h-screen with overflow-hidden above it. VehicleGrid used to
  // listen for WINDOW scroll (useWindowScroll), which barely ever fires
  // here, so infinite-scroll silently stalled after the first page or
  // two (whatever Virtuoso's initial overscan preloaded on mount) no
  // matter how far the user actually scrolled inside <main>. Passing
  // this ref down lets VehicleGrid track the real scroll container.
  const scrollParentRef = useRef<HTMLElement>(null);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex h-screen flex-col">
        <header className="flex shrink-0 items-center justify-between border-b border-hairline bg-panel px-4 py-2.5">
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
                {/* rtl:rotate-180 flips ← into → automatically under dir="rtl" — no JS branch needed */}
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
            <Hero visible={!selection} />
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

      <VehicleModal
        vehicle={openVehicle}
        onClose={() => setOpenVehicle(null)}
        translateEnabled={translateEnabled}
      />
    </QueryClientProvider>
  );
}
