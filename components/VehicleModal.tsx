"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useTranslations } from "next-intl";
import type { Vehicle } from "@/lib/types";
import { useTranslatedVehicle } from "@/hooks/useTranslatedVehicle";
import { CollapsibleSection } from "./CollapsibleSection";

// لیست کلیدهایی که از قبل جای ثابت در UI دارند و نباید به عنوان دیتای ناشناس رندر شوند
const KNOWN_KEYS = [
  "id", "name", "nation", "category", "rank", "isRare", "isEvent", "isPremium", "isSquadron",
  "br", "crew", "repairCost", "slMultiplier", "rpMultiplier", "mobility",
  "firepower", "armor", "avionics", "proTips", "sourceDetail", "dynamicSpecs"
];

// ---- دسته‌بندی خودکار هر فیلدی که ربات پیدا کرده ----
// این لیست فقط یه سرنخ کلمه‌ای برای هر دسته‌ست — به هیچ اسم فیلد خاصی
// وابسته نیست. اگه فردا اسکریپر یه فیلد کاملاً جدید پیدا کنه (مثلاً
// "wing_loading" یا "sonar_range")، خودش زیر یکی از همین دسته‌ها می‌شینه
// بدون اینکه لازم باشه کد اینجا عوض بشه.
const AUTO_SECTIONS: { title: string; eyebrow: string; match: RegExp }[] = [
  { title: "Armor & Survivability", eyebrow: "SURVIVABILITY", match: /armou?r|hull|turret|composite|\bera\b|survivab/i },
  { title: "Mobility", eyebrow: "MOBILITY", match: /speed|engine|power|weight|turn|climb|transmission|accel|mobility/i },
  { title: "Firepower", eyebrow: "ARMAMENT", match: /ammo|penetrat|reload|gun|cannon|rocket|missile|bomb|weapon|magazine|caliber/i },
  { title: "Avionics & Sensors", eyebrow: "SYSTEMS", match: /radar|thermal|\brwr\b|\blwr\b|avionic|targeting|sight|optic/i },
  { title: "Economy", eyebrow: "LOGISTICS", match: /research|purchase|cost|repair|multiplier|rp\b|\bsl\b/i },
  { title: "General", eyebrow: "OVERVIEW", match: /crew|visibility|role|country|rank|battle.?rating/i },
];

function categorize(key: string): { title: string; eyebrow: string } {
  const spaced = key.replace(/_/g, " ");
  for (const section of AUTO_SECTIONS) {
    if (section.match.test(spaced)) return section;
  }
  return { title: "Field Notes", eyebrow: "UNSORTED" };
}

function formatLabel(rawKey: string): string {
  return rawKey
    .replace(/_/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .trim()
    .replace(/^./, (c) => c.toUpperCase());
}

function formatValue(value: unknown): string {
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (Array.isArray(value)) return value.join(" · ");
  if (typeof value === "object" && value !== null) return JSON.stringify(value);
  return String(value);
}

export function VehicleModal({
  vehicle,
  onClose,
  translateEnabled,
}: {
  vehicle: Vehicle | null;
  onClose: () => void;
  translateEnabled: boolean;
}) {
  const t = useTranslations();
  const translation = useTranslatedVehicle(vehicle, translateEnabled);

  if (!vehicle) return null;

  const displayName = translation.data?.name ?? vehicle.name;
  const displayProTips = translation.data?.proTips ?? vehicle.proTips ?? [];

  // منبع فیلدهای خودسازمان‌ده: هم دیتای خام ویکی (dynamicSpecs) و هم هر
  // کلید سطح‌بالای ناشناس دیگه‌ای که ربات/دیتابیس اضافه کرده. یکی می‌شن
  // و بعد بر اساس کلمه‌ی کلیدی توی دسته‌ی مناسب قرار می‌گیرن.
  const rawSpecs = (vehicle.dynamicSpecs ?? {}) as Record<string, unknown>;
  const unknownTopLevel = Object.fromEntries(
    Object.keys(vehicle)
      .filter((key) => !KNOWN_KEYS.includes(key) && vehicle[key] !== null && vehicle[key] !== undefined)
      .map((key) => [key, vehicle[key]])
  );
  const allAutoFields: Record<string, unknown> = { ...rawSpecs, ...unknownTopLevel };

  const grouped = new Map<string, { eyebrow: string; entries: [string, unknown][] }>();
  for (const [key, value] of Object.entries(allAutoFields)) {
    if (value === null || value === undefined || value === "") continue;
    const { title, eyebrow } = categorize(key);
    if (!grouped.has(title)) grouped.set(title, { eyebrow, entries: [] });
    grouped.get(title)!.entries.push([key, value]);
  }
  // ترتیب ثابت و منطقی برای دسته‌ها (نه ترتیب تصادفی Map)
  const sectionOrder = ["General", "Armor & Survivability", "Firepower", "Mobility", "Avionics & Sensors", "Economy", "Field Notes"];
  const orderedGroups = sectionOrder
    .filter((title) => grouped.has(title))
    .map((title) => [title, grouped.get(title)!] as const);

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-ink/80 p-4 py-10 backdrop-blur-sm sm:items-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        role="dialog"
      >
        <motion.div
          layoutId={`card-${vehicle.id}`}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-2xl overflow-hidden rounded-sm border border-hairline bg-panel shadow-dossier"
        >
          {/* بخش هدر کارت */}
          <div className="relative h-36 w-full overflow-hidden bg-gradient-to-br from-panel2 to-ink sm:h-44">
            <button
              type="button"
              onClick={onClose}
              className="absolute end-3 top-3 flex h-8 w-8 items-center justify-center rounded-sm border border-hairline bg-ink/60 font-mono text-parchment/70 hover:border-brass hover:text-brass"
            >✕</button>
            <div className="absolute bottom-3 start-4 end-4">
              <p className="font-mono text-[10px] uppercase tracking-widest2 text-brass">
                {t(`nation.${vehicle.nation}`)} · Rk {vehicle.rank}
              </p>
              <h2 className="mt-1 text-start font-display text-2xl tracking-wide text-parchment sm:text-3xl">
                {displayName}
              </h2>
            </div>
          </div>

          {/* بخش اطلاعات ریتینگ (BR) */}
          <div className="grid grid-cols-3 divide-x divide-hairline border-b border-hairline">
            <BrStat label={t("modal.arcade")} value={vehicle.br.ab} />
            <BrStat label={t("modal.realistic")} value={vehicle.br.rb} />
            <BrStat label={t("modal.simulator")} value={vehicle.br.sb} />
          </div>

          <div className="max-h-[50vh] overflow-y-auto p-4 space-y-4">
            {/* بخش خدمه و آمار کلی (دیتای تمیزشده، همیشه اول) */}
            {(vehicle.crew || vehicle.mobility?.weightTons) && (
              <div className="grid grid-cols-2 gap-3 font-mono text-xs sm:grid-cols-3">
                {vehicle.crew ? (
                  <div className="flex flex-col border-l-2 border-brass/30 pl-2">
                    <span className="text-[10px] uppercase text-parchment/50">{t("modal.crew")}</span>
                    <span className="mt-0.5 text-sm font-bold text-parchment">
                      <bdi dir="ltr">{vehicle.crew}</bdi>
                    </span>
                  </div>
                ) : null}
                {vehicle.mobility?.weightTons ? (
                  <div className="flex flex-col border-l-2 border-brass/30 pl-2">
                    <span className="text-[10px] uppercase text-parchment/50">{"Weight"}</span>
                    <span className="mt-0.5 text-sm font-bold text-parchment">
                      <bdi dir="ltr">{vehicle.mobility.weightTons.toFixed(1)} t</bdi>
                    </span>
                  </div>
                ) : null}
              </div>
            )}

            {/* بخش آرمور — فقط وقتی حداقل یه مقدار واقعی داریم نمایش داده می‌شه */}
            {vehicle.armor && (vehicle.armor.hullFrontMm || vehicle.armor.turretFrontMm) && (
              <CollapsibleSection title={t("modal.sectionArmor")} eyebrow="SURVIVABILITY" defaultOpen>
                <div className="grid grid-cols-1 gap-3 font-mono text-xs sm:grid-cols-2">
                  {vehicle.armor.hullFrontMm ? (
                    <ArmorRow
                      label={"Hull"}
                      front={vehicle.armor.hullFrontMm}
                      side={vehicle.armor.hullSideMm}
                      back={vehicle.armor.hullRearMm}
                    />
                  ) : null}
                  {vehicle.armor.turretFrontMm ? (
                    <ArmorRow
                      label={"Turret"}
                      front={vehicle.armor.turretFrontMm}
                      side={vehicle.armor.turretSideMm}
                      back={vehicle.armor.turretRearMm}
                    />
                  ) : null}
                </div>
                {(vehicle.armor.composite || vehicle.armor.era) && (
                  <p className="mt-2 font-mono text-[10px] uppercase tracking-widest2 text-brass-dim">
                    {vehicle.armor.composite ? "Composite" : ""}
                    {vehicle.armor.composite && vehicle.armor.era ? " · " : ""}
                    {vehicle.armor.era ? "ERA" : ""}
                  </p>
                )}
              </CollapsibleSection>
            )}

            {/* بخش تسلیحات و مهمات با نفوذ در فواصل مختلف */}
            {vehicle.firepower?.ammoTypes && vehicle.firepower.ammoTypes.length > 0 && (
              <CollapsibleSection title={t("modal.sectionFirepower")} eyebrow="ARMAMENT" defaultOpen>
                <div className="space-y-3">
                  {vehicle.firepower.reloadBaseSec ? (
                    <p className="font-mono text-xs text-parchment/70">
                      {"Reload"}:{" "}
                      <bdi dir="ltr">
                        {vehicle.firepower.reloadBaseSec}s → {vehicle.firepower.reloadAcedSec}s
                      </bdi>
                    </p>
                  ) : null}
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse font-mono text-[11px]">
                      <thead>
                        <tr className="border-b border-hairline text-parchment/50">
                          <th className="py-1 text-start font-normal">{"Round"}</th>
                          <th className="py-1 text-start font-normal">{"Type"}</th>
                          <th className="py-1 text-end font-normal">10m</th>
                          <th className="py-1 text-end font-normal">500m</th>
                          <th className="py-1 text-end font-normal">1000m</th>
                          <th className="py-1 text-end font-normal">2000m</th>
                        </tr>
                      </thead>
                      <tbody>
                        {vehicle.firepower.ammoTypes.map((round: any, i: number) => (
                          <tr key={i} className="border-b border-hairline/40 text-parchment">
                            <td className="py-1 text-start">{round.name}</td>
                            <td className="py-1 text-start text-parchment/60">{round.type}</td>
                            {["10m", "500m", "1000m", "2000m"].map((r) => (
                              <td key={r} className="py-1 text-end">
                                <bdi dir="ltr">
                                  {round.penetration?.find((p: any) => `${p.rangeM}m` === r)?.angle0 ??
                                    round[r] ??
                                    "—"}
                                </bdi>
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </CollapsibleSection>
            )}

            {/* ---- بخش‌های خودسازمان‌ده: هر چیزی که ربات پیدا کرده و بالا
                 پوشش داده نشده، خودش بر اساس کلمه‌ی کلیدی توی دسته‌ی
                 مناسب می‌شینه. فیلد جدید = بدون تغییر کد، خودکار جاش پیدا
                 می‌شه. ---- */}
            {orderedGroups.map(([title, group]) => (
              <CollapsibleSection key={title} title={title} eyebrow={group.eyebrow}>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 font-mono text-xs">
                  {group.entries.map(([key, value]) => (
                    <div key={key} className="flex flex-col border-l-2 border-brass/30 pl-2">
                      <span className="text-[10px] uppercase text-parchment/50">{formatLabel(key)}</span>
                      <span className="mt-0.5 text-sm font-bold text-parchment">
                        <bdi dir="ltr">{formatValue(value)}</bdi>
                      </span>
                    </div>
                  ))}
                </div>
              </CollapsibleSection>
            ))}

            {/* بخش نکات حرفه‌ای (Pro Tips) */}
            {displayProTips.length > 0 && (
              <CollapsibleSection title={t("modal.sectionProTips")} eyebrow={t("modal.fieldNotes")}>
                <ul className="list-inside list-disc space-y-1 text-start font-body text-sm text-parchment/75">
                  {displayProTips.map((tip: string, i: number) => (
                    <li key={i}>{tip}</li>
                  ))}
                </ul>
              </CollapsibleSection>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

// کامپوننت کمکی برای نمایش یک ردیف آرمور (جلو/کنار/عقب)
function ArmorRow({
  label,
  front,
  side,
  back,
}: {
  label: string;
  front?: number;
  side?: number;
  back?: number;
}) {
  return (
    <div className="flex flex-col border-l-2 border-brass/30 pl-2">
      <span className="text-[10px] uppercase text-parchment/50">{label}</span>
      <span className="mt-0.5 text-sm font-bold text-parchment">
        <bdi dir="ltr">
          {front ?? "—"} / {side ?? "—"} / {back ?? "—"} mm
        </bdi>
      </span>
    </div>
  );
}

// کامپوننت کمکی برای نمایش BR
function BrStat({ label, value }: { label: string; value: number }) {
  return (
    <div className="px-3 py-2.5 text-center">
      <p className="font-mono text-[9px] uppercase tracking-widest2 text-parchment/40">{label}</p>
      <p className="font-mono text-lg text-brass">
        <bdi dir="ltr">{value.toFixed(1)}</bdi>
      </p>
    </div>
  );
}
