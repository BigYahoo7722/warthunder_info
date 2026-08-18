"use client";

import { useQuery } from "@tanstack/react-query";
import { useLocale } from "next-intl";
import type { Vehicle } from "@/lib/types";

export interface TranslatedVehicleFields {
  name: string;
  proTips: string[];
  moduleNotes?: string;
}

async function translateTexts(texts: string[], targetLocale: string): Promise<string[]> {
  const res = await fetch("/api/translate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texts, targetLocale }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}) as Record<string, string>);
    throw new Error(body.message || body.error || `Translate request failed: ${res.status}`);
  }
  const data = await res.json();
  return data.translations as string[];
}

/**
 * Translates the parts of a Vehicle record that come from raw pipeline
 * data rather than the UI's own message files: name, pro-tips, and armor
 * module notes. Everything else in the modal (section labels, stat names
 * like "Top speed") is already localized via next-intl's messages/*.json —
 * this hook only covers the dynamic payload next-intl can't know about
 * ahead of time, per the brief's Phase 5.
 *
 * Cached by React Query on (vehicle id, locale), so toggling translation
 * on/off or reopening the same vehicle doesn't re-hit the API — DeepL's
 * free tier has a monthly character cap, so avoiding redundant calls isn't
 * just a latency nicety here.
 */
export function useTranslatedVehicle(vehicle: Vehicle | null, enabled: boolean) {
  const locale = useLocale();

  return useQuery({
    queryKey: ["vehicle-translation", vehicle?.id, locale],
    queryFn: async (): Promise<TranslatedVehicleFields> => {
      if (!vehicle) throw new Error("No vehicle selected");
      const hasModuleNotes = Boolean(vehicle.armor?.moduleNotes);
      const texts = [
        vehicle.name,
        ...vehicle.proTips,
        ...(hasModuleNotes ? [vehicle.armor!.moduleNotes as string] : []),
      ];
      const translated = await translateTexts(texts, locale);
      const [name, ...rest] = translated;
      const proTips = rest.slice(0, vehicle.proTips.length);
      const moduleNotes = hasModuleNotes ? rest[vehicle.proTips.length] : undefined;
      return { name, proTips, moduleNotes };
    },
    enabled: enabled && Boolean(vehicle) && locale !== "en",
    staleTime: 24 * 60 * 60 * 1000, // translations are static for a given (text, locale) pair
    retry: 1,
  });
}
