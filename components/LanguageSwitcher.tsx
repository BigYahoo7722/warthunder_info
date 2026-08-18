"use client";

import { useLocale, useTranslations } from "next-intl";
import { useRouter, usePathname } from "@/i18n/navigation";
import { LOCALES, LOCALE_LABELS, type AppLocale } from "@/i18n/routing";

export function LanguageSwitcher() {
  const t = useTranslations("language");
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  return (
    <label className="flex items-center gap-1.5">
      <span className="sr-only">{t("label")}</span>
      <select
        value={locale}
        onChange={(e) => {
          router.replace(pathname, { locale: e.target.value as AppLocale });
        }}
        className="tab-cut border-l-2 border-hairline bg-panel2 py-1 pe-6 ps-2 font-mono text-[11px] uppercase tracking-wide text-parchment/70 outline-none transition-colors hover:border-brass-dim focus-visible:border-brass"
      >
        {LOCALES.map((l) => (
          <option key={l} value={l} className="bg-panel2 text-parchment">
            {LOCALE_LABELS[l]}
          </option>
        ))}
      </select>
    </label>
  );
}
