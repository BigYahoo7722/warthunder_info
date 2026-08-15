import type { Category, Nation } from "./types";

export interface NationMeta {
  id: Nation;
  label: string;
  flag: string;
}

export interface CategoryMeta {
  id: Category;
  label: string;
  icon: string;
}

// Unicode has no dedicated USSR flag glyph, so the Russian Federation flag
// stands in for the Soviet tech tree — the same convention every War
// Thunder fan site and the game's own launcher-adjacent tools use.
export const NATIONS: NationMeta[] = [
  { id: "usa", label: "USA", flag: "🇺🇸" },
  { id: "germany", label: "Germany", flag: "🇩🇪" },
  { id: "ussr", label: "USSR", flag: "🇷🇺" },
  { id: "britain", label: "Britain", flag: "🇬🇧" },
  { id: "japan", label: "Japan", flag: "🇯🇵" },
  { id: "china", label: "China", flag: "🇨🇳" },
  { id: "italy", label: "Italy", flag: "🇮🇹" },
  { id: "france", label: "France", flag: "🇫🇷" },
  { id: "sweden", label: "Sweden", flag: "🇸🇪" },
  { id: "israel", label: "Israel", flag: "🇮🇱" },
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
