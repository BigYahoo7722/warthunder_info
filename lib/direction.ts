"use client";

import { useLocale } from "next-intl";
import { isRtl } from "@/i18n/routing";

export function useDirection(): "ltr" | "rtl" {
  const locale = useLocale();
  return isRtl(locale) ? "rtl" : "ltr";
}

/**
 * Framer Motion's `x` transform is a physical pixel offset, not a logical
 * CSS property — unlike `inset-inline-start` or a plain `flex-row` layout
 * (which both auto-mirror under `dir="rtl"` for free), a `motion.div`
 * animating `x: -32` will always slide in from the *visual* left, even when
 * the page has been mirrored to RTL and that edge is now the trailing edge.
 * Wrap any hardcoded slide offset in this so it flips sign under RTL and
 * slides in from the correct (now-opposite) physical side.
 *
 * Everything else in this app's RTL handling — sidebar order, text
 * alignment, drawer position — uses logical Tailwind utilities (start- and
 * end- prefixed classes, text-start/text-end) instead of this, on purpose:
 * logical properties are the more robust default and don't need a JS
 * branch per usage. This hook exists only for the one thing that has no
 * logical equivalent.
 */
export function useRtlFlip() {
  const dir = useDirection();
  return (x: number) => (dir === "rtl" ? -x : x);
}
