"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useTranslations } from "next-intl";
import type { Vehicle } from "@/lib/types";
import { useTranslatedVehicle } from "@/hooks/useTranslatedVehicle";
import { CollapsibleSection } from "./CollapsibleSection";

const staggerContainer = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.04, delayChildren: 0.1 },
  },
};

const fadeUpItem = {
  hidden: { opacity: 0, y: 6, scale: 0.98 },
  show: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    transition: { type: "spring", stiffness: 300, damping: 24 }
  },
};

// لیست کلیدهایی که از قبل جای ثابت در UI دارند
const KNOWN_KEYS = [
  "id", "name", "nation", "category", "rank", "isRare", "isEvent", "isPremium", "isSquadron",
  "br", "crew", "repairCost", "slMultiplier", "rpMultiplier", "mobility", 
  "firepower", "armor", "avionics", "proTips", "sourceDetail"
];

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

  // استخراج تمام کلیدهای غیرمنتظره و اضافه که در JSON وجود دارند
  const dynamicKeys = Object.keys(vehicle).filter(
    (key) => !KNOWN_KEYS.includes(key) && vehicle[key] !== null && vehicle[key] !== undefined
  );

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
          {/* Header */}
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

          {/* BR Stats */}
          <div className="grid grid-cols-3 divide-x divide-hairline border-b border-hairline">
            <BrStat label={t("modal.arcade")} value={vehicle.br.ab} />
            <BrStat label={t("modal.realistic")} value={vehicle.br.rb} />
            <BrStat label={t("modal.simulator")} value={vehicle.br.sb} />
          </div>

          <div className="max-h-[50vh] overflow-y-auto p-4 space-y-4">
            {/* رندر خودکار تمام کادرهای جدید و غیرمنتظره */}
            {dynamicKeys.length > 0 && (
              <CollapsibleSection title="اطلاعات تکمیلی" eyebrow="DYNAMIC DATA" defaultOpen>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 font-mono text-xs">
                  {dynamicKeys.map((key) => (
                    <DynamicStat key={key} rawKey={key} value={vehicle[key]} />
                  ))}
                </div>
              </CollapsibleSection>
            )}

            {/* Pro Tips */}
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

function DynamicStat({ rawKey, value }: { rawKey: string; value: any }) {
  // تبدیل اسم کلید مثل favoriteFood به Favorite Food
  const formattedLabel = rawKey
    .replace(/([A-Z])/g, " $1")
    .trim()
    .replace(/^./, (str) => str.toUpperCase());

  let displayValue = "";
  if (typeof value === "boolean") displayValue = value ? "Yes" : "No";
  else if (Array.isArray(value)) displayValue = value.join(" · ");
  else if (typeof value === "object" && value !== null) displayValue = JSON.stringify(value);
  else displayValue = String(value);

  return (
    <div className="flex flex-col border-l-2 border-brass/30 pl-2">
      <span className="text-[10px] text-parchment/50 uppercase">{formattedLabel}</span>
      <span className="text-sm text-parchment font-bold mt-0.5">
        <bdi dir="ltr">{displayValue}</bdi>
      </span>
    </div>
  );
}

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
