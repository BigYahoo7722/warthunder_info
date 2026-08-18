"use client";

import { useLocale, useTranslations } from "next-intl";

export function TranslateToggle({
  enabled,
  onChange,
}: {
  enabled: boolean;
  onChange: (value: boolean) => void;
}) {
  const t = useTranslations("language");
  const locale = useLocale();

  if (locale === "en") return null; // nothing to translate into

  return (
    <label className="flex cursor-pointer items-center gap-2 font-mono text-[11px] uppercase tracking-wide text-parchment/70">
      <span className="hidden sm:inline">{t("translateToggle")}</span>
      <span
        role="switch"
        aria-checked={enabled}
        tabIndex={0}
        onClick={() => onChange(!enabled)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            onChange(!enabled);
          }
        }}
        className={`relative h-4 w-8 shrink-0 rounded-full border transition-colors ${
          enabled ? "border-brass bg-brass/30" : "border-hairline bg-panel2"
        }`}
      >
        <span
          className={`absolute top-0.5 h-2.5 w-2.5 rounded-full bg-brass transition-transform ${
            enabled ? "translate-x-[18px] rtl:-translate-x-[18px]" : "translate-x-0.5 rtl:-translate-x-0.5"
          }`}
        />
      </span>
    </label>
  );
}
