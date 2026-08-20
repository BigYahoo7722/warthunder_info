import type { Category, Nation } from "./types";

export interface NationMeta {
  id: Nation;
  label: string;
  flag: string; // emoji, kept as an accessible/alt fallback — NOT rendered directly (see note below)
  flagIso: string; // ISO 3166-1 alpha-2, used to render a real flag image via flagcdn.com
}

export interface CategoryMeta {
  id: Category;
  label: string;
  icon: string;
}

// FIX: nation.flag ("🇺🇸" etc.) used to be rendered directly as text in
// Sidebar.tsx. Flag emoji require an OS-level color-flag font — Android
// and iOS both ship one, so it renders correctly on phones, but Windows +
// Chrome/Edge has no such font and silently falls back to the raw
// two-letter regional-indicator text ("US", "DE", ...) instead of a flag
// glyph. That's exactly what showed up in the sidebar on a Windows
// desktop. flagIso feeds a real <img> (see components/Sidebar.tsx),
// which renders identically on every OS/browser. flag is kept only as
// the image's alt text / accessible name.
//
// Unicode has no dedicated USSR flag glyph, so the Russian Federation flag
// stands in for the Soviet tech tree — the same convention every War
// Thunder fan site and the game's own launcher-adjacent tools use.
export const NATIONS: NationMeta[] = [
  { id: "usa", label: "USA", flag: "🇺🇸", flagIso: "us" },
  { id: "germany", label: "Germany", flag: "🇩🇪", flagIso: "de" },
  { id: "ussr", label: "USSR", flag: "🇷🇺", flagIso: "ru" },
  { id: "britain", label: "Britain", flag: "🇬🇧", flagIso: "gb" },
  { id: "japan", label: "Japan", flag: "🇯🇵", flagIso: "jp" },
  { id: "china", label: "China", flag: "🇨🇳", flagIso: "cn" },
  { id: "italy", label: "Italy", flag: "🇮🇹", flagIso: "it" },
  { id: "france", label: "France", flag: "🇫🇷", flagIso: "fr" },
  { id: "sweden", label: "Sweden", flag: "🇸🇪", flagIso: "se" },
  { id: "israel", label: "Israel", flag: "🇮🇱", flagIso: "il" },
];

export const CATEGORIES: CategoryMeta[] = [
  { id: "aviation", label: "Aviation", icon: "✈" },
  { id: "army", label: "Army", icon: "🐅" },
  { id: "fleet", label: "Fleet", icon: "⚓" },
  { id: "helicopters", label: "Helicopters", icon: "🚁" },
];

export function nationLabel(id: Nation): string {
  return NATIONS.find((n) => n.id === id)?.label ?? id;
}
