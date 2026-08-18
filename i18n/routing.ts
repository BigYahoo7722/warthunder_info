import { defineRouting } from "next-intl/routing";

// The two RTL locales are called out explicitly in the brief (Persian +
// Arabic) — direction.ts and every component that positions things with an
// explicit x/left/right value (not a logical CSS property) reads from
// RTL_LOCALES, so adding a locale here is the one place that needs touching
// to bring a new RTL language online.
export const LOCALES = [
  "en", "fa", "ar", "es", "zh", "ru", "de", "fr",
  "ja", "ko", "it", "pt", "hi", "tr", "vi", "pl",
] as const;

export type AppLocale = (typeof LOCALES)[number];

export const RTL_LOCALES: readonly AppLocale[] = ["fa", "ar"];

export const DEFAULT_LOCALE: AppLocale = "en";

export const LOCALE_LABELS: Record<AppLocale, string> = {
  en: "English",
  fa: "فارسی",
  ar: "العربية",
  es: "Español",
  zh: "简体中文",
  ru: "Русский",
  de: "Deutsch",
  fr: "Français",
  ja: "日本語",
  ko: "한국어",
  it: "Italiano",
  pt: "Português",
  hi: "हिन्दी",
  tr: "Türkçe",
  vi: "Tiếng Việt",
  pl: "Polski",
};

export function isRtl(locale: string): boolean {
  return (RTL_LOCALES as readonly string[]).includes(locale);
}

export const routing = defineRouting({
  locales: LOCALES,
  defaultLocale: DEFAULT_LOCALE,
  localePrefix: "as-needed", // default locale (en) has no /en prefix; others get /fa, /ar, etc.
});
