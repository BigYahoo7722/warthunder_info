import type { AppLocale } from "@/i18n/routing";

export interface FontRoles {
  display: string; // headlines, vehicle names, badges — used sparingly
  body: string; // UI copy, descriptions, pro-tips prose
  mono: string; // stats, BR numbers, status lines — always Latin/digits only,
  // so this never needs script-specific glyph coverage even in non-Latin
  // locales (see note on NUMERIC_MONO_LOCALES below).
  googleFontsParams: string[]; // family=...  segments, deduped per locale group
}

// Script groups, each with real font choices (not just "pick something
// Latin for everything" — Cyrillic, Persian/Arabic, and CJK all need actual
// glyph coverage for the *display* and *body* roles, since those render
// real translated prose, not just digits).
const LATIN: FontRoles = {
  display: "Staatliches, sans-serif",
  body: '"IBM Plex Sans", sans-serif',
  mono: '"Share Tech Mono", monospace',
  googleFontsParams: [
    "family=Staatliches",
    "family=IBM+Plex+Sans:wght@400;500;600",
    "family=Share+Tech+Mono",
  ],
};

const CYRILLIC: FontRoles = {
  // Staatliches' Cyrillic glyph coverage isn't something I could verify in
  // this build's sandbox (no browsable Google Fonts specimen access), so
  // this deliberately doesn't gamble on it for Russian body/display text.
  // Oswald has confirmed broad Cyrillic support and keeps the same
  // condensed/technical feel. Confirm before shipping if this matters to
  // you — worst case a missing-glyph fallback is a readability bug, not a
  // crash, but it's still worth a five-minute check on fonts.google.com.
  display: "Oswald, sans-serif",
  body: '"IBM Plex Sans", sans-serif',
  mono: '"Share Tech Mono", monospace',
  googleFontsParams: [
    "family=Oswald:wght@500;700",
    "family=IBM+Plex+Sans:wght@400;500;600",
    "family=Share+Tech+Mono",
  ],
};

const PERSIAN_ARABIC: FontRoles = {
  display: "Vazirmatn, sans-serif",
  body: "Vazirmatn, sans-serif",
  mono: '"Share Tech Mono", monospace', // stat VALUES stay Latin-numeral even in RTL, see note below
  googleFontsParams: ["family=Vazirmatn:wght@400;500;700;900", "family=Share+Tech+Mono"],
};

const CJK: (family: string) => FontRoles = (family) => ({
  display: `"${family}", sans-serif`,
  body: `"${family}", sans-serif`,
  mono: '"Share Tech Mono", monospace',
  googleFontsParams: [`family=${family.replace(/ /g, "+")}:wght@400;500;700;900`, "family=Share+Tech+Mono"],
});

const DEVANAGARI: FontRoles = {
  display: '"Noto Sans Devanagari", sans-serif',
  body: '"Noto Sans Devanagari", sans-serif',
  mono: '"Share Tech Mono", monospace',
  googleFontsParams: ["family=Noto+Sans+Devanagari:wght@400;500;700;900", "family=Share+Tech+Mono"],
};

export const FONT_ROLES: Record<AppLocale, FontRoles> = {
  en: LATIN,
  es: LATIN,
  de: LATIN,
  fr: LATIN,
  it: LATIN,
  pt: LATIN,
  tr: LATIN,
  vi: LATIN,
  pl: LATIN,
  ru: CYRILLIC,
  fa: PERSIAN_ARABIC,
  ar: PERSIAN_ARABIC,
  zh: CJK("Noto Sans SC"),
  ja: CJK("Noto Sans JP"),
  ko: CJK("Noto Sans KR"),
  hi: DEVANAGARI,
};

export function googleFontsHref(locale: AppLocale): string {
  const params = FONT_ROLES[locale].googleFontsParams.join("&");
  return `https://fonts.googleapis.com/css2?${params}&display=swap`;
}

/**
 * CSS custom properties consumed by tailwind.config.ts (fontFamily.display /
 * .body / .mono resolve to var(--font-display) etc). Setting these per
 * request on <body style={...}> is what makes `font-display`/`font-body`/
 * `font-mono` utility classes resolve to the right typeface per locale
 * without a build-time branch for every locale.
 */
export function fontCssVars(locale: AppLocale): React.CSSProperties {
  const roles = FONT_ROLES[locale];
  return {
    ["--font-display" as string]: roles.display,
    ["--font-body" as string]: roles.body,
    ["--font-mono" as string]: roles.mono,
  };
}
