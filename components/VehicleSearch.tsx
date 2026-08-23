"use client";

import { useEffect, useRef, useState } from "react";
import type { Category, Nation } from "@/lib/types";
import type { SearchResult } from "@/app/api/vehicles/search/route";

const DEBOUNCE_MS = 250;

export function VehicleSearch({
  onSelect,
}: {
  onSelect: (nation: Nation, category: Category) => void;
}) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    const trimmed = query.trim();
    if (trimmed.length < 1) {
      setResults([]);
      setOpen(false);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await fetch(`/api/vehicles/search?q=${encodeURIComponent(trimmed)}`);
        const data = await res.json();
        setResults(data.items ?? []);
        setOpen(true);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, DEBOUNCE_MS);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query]);

  // بستن نتایج با کلیک بیرون از باکس جستجو
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleSelect(item: SearchResult) {
    setQuery(item.name);
    setOpen(false);
    onSelect(item.nation as Nation, item.category as Category);
  }

  return (
    <div ref={containerRef} className="relative mx-auto w-full max-w-md px-4">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => results.length > 0 && setOpen(true)}
        placeholder="Search vehicles…"
        className="w-full rounded-sm border border-hairline bg-panel px-3.5 py-2.5 text-start font-mono text-sm text-parchment placeholder:text-parchment/40 focus:border-brass focus:outline-none"
        // FIX: with no explicit "search" role/keyboard handling this input
        // was fully mouse-only; Enter now opens the top result, matching
        // what a person expects from any search box.
        onKeyDown={(e) => {
          if (e.key === "Enter" && results.length > 0) {
            handleSelect(results[0]);
          }
          if (e.key === "Escape") setOpen(false);
        }}
      />

      {open && (
        <div className="absolute inset-x-4 top-full z-20 mt-1 max-h-80 overflow-y-auto rounded-sm border border-hairline bg-panel shadow-dossier">
          {loading && (
            <p className="p-3 font-mono text-[11px] uppercase tracking-widest2 text-parchment/40">
              {"Searching…"}
            </p>
          )}
          {!loading && results.length === 0 && (
            <p className="p-3 font-mono text-[11px] uppercase tracking-widest2 text-parchment/40">
              {"No matches"}
            </p>
          )}
          {!loading &&
            results.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => handleSelect(item)}
                className="flex w-full items-center justify-between border-b border-hairline/40 px-3.5 py-2 text-start last:border-b-0 hover:bg-panel2"
              >
                <span className="font-body text-sm text-parchment">{item.name}</span>
                <span className="font-mono text-[10px] uppercase tracking-widest2 text-parchment/40">
                  <bdi dir="ltr">
                    {item.nation} · Rk {item.rank ?? "—"}
                  </bdi>
                </span>
              </button>
            ))}
        </div>
      )}
    </div>
  );
}
