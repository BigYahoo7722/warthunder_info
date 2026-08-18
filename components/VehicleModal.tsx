"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useTranslations } from "next-intl";
import type { Vehicle } from "@/lib/types";
import { useTranslatedVehicle } from "@/hooks/useTranslatedVehicle";
import { useRealtimeVehicle } from "@/hooks/useRealtimeVehicle";
import { CollapsibleSection } from "./CollapsibleSection";

// تنظیمات انیمیشن
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

// لیست کلیدهای استاتیک که از قبل براشون UI ساختیم
const KNOWN_KEYS = [
  "id", "name", "nation", "rank", "isRare", "isEvent", "br", "crew",
  "repairCost", "slMultiplier", "rpMultiplier", "mobility", 
  "firepower", "armor", "avionics", "proTips", "moduleNotes", "class"
];

export function VehicleModal({
  vehicle: initialVehicle,
  onClose,
  translateEnabled,
}: {
  vehicle: Vehicle | null;
  onClose: () => void;
  translateEnabled: boolean;
}) {
  const t = useTranslations();
  const liveVehicle = useRealtimeVehicle(initialVehicle); 
  const activeVehicle = liveVehicle || initialVehicle;
  const translation = useTranslatedVehicle(activeVehicle, translateEnabled);

  const displayName = translation.data?.name ?? activeVehicle?.name;
  const displayProTips = translation.data?.proTips ?? activeVehicle?.proTips ?? [];
  const displayModuleNotes = translation.data?.moduleNotes ?? activeVehicle?.armor?.moduleNotes;

  // استخراج خودکار تمام دیتای ناشناس و جدیدی که ربات اضافه کرده است
  const dynamicKeys = activeVehicle 
    ? Object.keys(activeVehicle).filter(key => !KNOWN_KEYS.includes(key) && activeVehicle[key] !== null && activeVehicle[key] !== undefined)
    : [];

  return (
    <AnimatePresence>
      {activeVehicle && (
        <motion.div
          className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-ink/80 p-4 py-10 backdrop-blur-sm sm:items-center"
          initial={{ opacity: 0, backdropFilter: "blur(0px)" }}
          animate={{ opacity: 1, backdropFilter: "blur(4px)" }}
          exit={{ opacity: 0, backdropFilter: "blur(0px)" }}
          transition={{ duration: 0.3 }}
          onClick={onClose}
          role="dialog"
        >
          <motion.div
            layoutId={`card-${activeVehicle.id}`}
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-2xl overflow-hidden rounded-sm border border-hairline bg-panel shadow-dossier"
            transition={{ type: "spring", bounce: 0.15, duration: 0.5 }}
          >
            {/* Header Section */}
            <motion.div
              layoutId={`card-plate-${activeVehicle.id}`}
              className="relative h-36 w-full overflow-hidden bg-gradient-to-br from-panel2 to-ink sm:h-44"
            >
              <motion.div 
                className="absolute inset-0 opacity-[0.08] [background-image:repeating-linear-gradient(115deg,transparent,transparent_10px,#E8E4D6_10px,#E8E4D6_11px)]"
                animate={{ backgroundPosition: ["0px 0px", "20px 20px"] }}
                transition={{ duration: 4, repeat: Infinity, repeatType: "reverse", ease: "linear" }}
              />
              <button
                type="button"
                onClick={onClose}
                className="absolute end-3 top-3 flex h-8 w-8 items-center justify-center rounded-sm border border-hairline bg-ink/60 font-mono text-parchment/70 transition-all hover:scale-105 hover:border-brass hover:text-brass"
              >✕</button>
              <div className="absolute bottom-3 start-4 end-4">
                <p className="font-mono text-[10px] uppercase tracking-widest2 text-brass">
                  {t(`nation.${activeVehicle.nation}`)} · Rk {activeVehicle.rank}
                  {liveVehicle && <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="ms-2 inline-flex h-1.5 w-1.5 rounded-full bg-green-500 shadow-[0_0_6px_#22c55e]" />}
                </p>
                <motion.h2 layout="position" className="mt-1 text-start font-display text-2xl tracking-wide text-parchment sm:text-3xl">
                  {displayName}
                </motion.h2>
              </div>
            </motion.div>

            {/* Static Content (BR, Economy) */}
            <motion.div variants={staggerContainer} initial="hidden" animate="show" className="grid grid-cols-3 divide-x divide-hairline border-b border-hairline">
              <BrStat label={t("modal.arcade")} value={activeVehicle.br.ab} />
              <BrStat label={t("modal.realistic")} value={activeVehicle.br.rb} />
              <BrStat label={t("modal.simulator")} value={activeVehicle.br.sb} />
            </motion.div>

            <div className="max-h-[50vh] overflow-y-auto overflow-x-hidden p-1">
              <AnimatePresence mode="popLayout">
                {/* بخش‌های استاتیک قبلی (Mobility, Firepower, Armor, Avionics) اینجا قرار می‌گیرند... */}
                {/* برای خلاصه بودن کد، فرض کنید کدهای CollapsibleSection مربوط به mobility و firepower را اینجا گذاشته‌اید */}

                {/* --- ارگانیسم زنده: رندر خودکار دیتای ناشناس و جدید --- */}
                {dynamicKeys.length > 0 && (
                  <CollapsibleSection key="dynamic-data" title="Classified Intel" eyebrow="RAW DATA" defaultOpen>
                    <motion.dl variants={staggerContainer} initial="hidden" animate="show" className="grid grid-cols-1 gap-x-4 gap-y-3 font-mono text-xs sm:grid-cols-2">
                      {dynamicKeys.map((key) => (
                        <DynamicStat 
                          key={key} 
                          rawKey={key} 
                          value={activeVehicle[key]} 
                        />
                      ))}
                    </motion.dl>
                  </CollapsibleSection>
                )}

                {/* Pro Tips Section */}
                <CollapsibleSection key="protips" title={t("modal.sectionProTips")} eyebrow={t("modal.fieldNotes")}>
                  <motion.ul variants={staggerContainer} initial="hidden" animate="show" className="list-inside list-disc space-y-1.5 text-start font-body text-sm leading-snug text-parchment/75">
                    {displayProTips.map((tip: string, i: number) => (
                      <motion.li variants={fadeUpItem} key={i}>{tip}</motion.li>
                    ))}
                  </motion.ul>
                </CollapsibleSection>
              </AnimatePresence>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// کامپوننت هوشمند برای مدیریت انواع مختلف داده‌های ناشناس
function DynamicStat({ rawKey, value }: { rawKey: string; value: any }) {
  // تبدیل camelCase به کلمات جداگانه با حرف اول بزرگ (مثلا pilotFavoriteFood -> Pilot Favorite Food)
  const formattedLabel = rawKey.replace(/([A-Z])/g, ' $1').trim().replace(/^./, (str) => str.toUpperCase());

  let displayValue = "";
  
  // تشخیص هوشمند نوع دیتا برای نمایش صحیح
  if (typeof value === "boolean") {
    displayValue = value ? "Yes" : "No";
  } else if (Array.isArray(value)) {
    displayValue = value.join(" · "); // آرایه‌ها رو با نقطه به هم می‌چسبونه
  } else if (typeof value === "object" && value !== null) {
    displayValue = JSON.stringify(value); // اگه آبجکت تو در تو بود
  } else {
    displayValue = String(value); // اعداد و استرینگ‌های معمولی
  }

  return (
    <motion.div variants={fadeUpItem} layout className="group flex flex-col justify-start border-l-2 border-brass/20 pl-2">
      <dt className="text-[10px] tracking-wider text-parchment/40 uppercase transition-colors group-hover:text-parchment/60">
        {formattedLabel}
      </dt>
      <motion.dd 
        key={displayValue}
        initial={{ opacity: 0.5, x: -5 }}
        animate={{ opacity: 1, x: 0 }}
        className="mt-0.5 text-sm text-parchment transition-colors group-hover:text-brass"
      >
        <bdi dir="ltr">{displayValue}</bdi>
      </motion.dd>
    </motion.div>
  );
}

function BrStat({ label, value }: { label: string; value: number }) {
  return (
    <motion.div variants={fadeUpItem} className="px-3 py-2.5 text-center">
      <p className="font-mono text-[9px] uppercase tracking-widest2 text-parchment/40">{label}</p>
      <motion.p key={value} initial={{ scale: 1.2, color: "#fff" }} animate={{ scale: 1, color: "var(--brass, #eab308)" }} className="font-mono text-lg">
        <bdi dir="ltr">{value.toFixed(1)}</bdi>
      </motion.p>
    </motion.div>
  );
}
