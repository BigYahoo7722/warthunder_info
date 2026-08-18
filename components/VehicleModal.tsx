"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useTranslations } from "next-intl";
import type { Vehicle } from "@/lib/types";
import { useTranslatedVehicle } from "@/hooks/useTranslatedVehicle";
import { useRealtimeVehicle } from "@/hooks/useRealtimeVehicle"; // هوک جدید برای اتصال مستقیم به سوپابیس
import { CollapsibleSection } from "./CollapsibleSection";

// تنظیمات انیمیشن‌های ارگانیک و آبشاری برای هماهنگی و زنده بودن فرم
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

export function VehicleModal({
  vehicle: initialVehicle, // دیتای اولیه تغییر نام داد تا با دیتای زنده جایگزین بشه
  onClose,
  translateEnabled,
}: {
  vehicle: Vehicle | null;
  onClose: () => void;
  translateEnabled: boolean;
}) {
  const t = useTranslations();
  
  // ارگانیسم زنده: گوش دادن به تغییراتی که ربات مستقیماً در سوپابیس اعمال می‌کند
  const liveVehicle = useRealtimeVehicle(initialVehicle); 
  const activeVehicle = liveVehicle || initialVehicle;

  const translation = useTranslatedVehicle(activeVehicle, translateEnabled);

  const displayName = translation.data?.name ?? activeVehicle?.name;
  const displayProTips = translation.data?.proTips ?? activeVehicle?.proTips ?? [];
  const displayModuleNotes = translation.data?.moduleNotes ?? activeVehicle?.armor?.moduleNotes;

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
          aria-modal="true"
          aria-label={displayName}
        >
          <motion.div
            layoutId={`card-${activeVehicle.id}`}
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-2xl overflow-hidden rounded-sm border border-hairline bg-panel shadow-dossier"
            // افکت فنری ملایم برای ورود مدال تا حس خشکی نداشته باشد
            transition={{ type: "spring", bounce: 0.15, duration: 0.5 }}
          >
            <motion.div
              layoutId={`card-plate-${activeVehicle.id}`}
              className="relative h-36 w-full overflow-hidden bg-gradient-to-br from-panel2 to-ink sm:h-44"
            >
              {/* افکت تنفس (Breathing) در بک‌گراند برای القای حس زنده بودن */}
              <motion.div 
                className="absolute inset-0 opacity-[0.08] [background-image:repeating-linear-gradient(115deg,transparent,transparent_10px,#E8E4D6_10px,#E8E4D6_11px)]"
                animate={{ backgroundPosition: ["0px 0px", "20px 20px"] }}
                transition={{ duration: 4, repeat: Infinity, repeatType: "reverse", ease: "linear" }}
              />
              
              <button
                type="button"
                onClick={onClose}
                aria-label={t("modal.close")}
                className="absolute end-3 top-3 flex h-8 w-8 items-center justify-center rounded-sm border border-hairline bg-ink/60 font-mono text-parchment/70 transition-all hover:scale-105 hover:border-brass hover:text-brass hover:shadow-[0_0_8px_rgba(var(--brass-rgb),0.3)]"
              >
                ✕
              </button>
              
              <div className="absolute bottom-3 start-4 end-4">
                <p className="font-mono text-[10px] uppercase tracking-widest2 text-brass">
                  {t(`nation.${activeVehicle.nation}`)} · Rk {activeVehicle.rank}
                  {activeVehicle.isRare && ` · ${t("modal.rareAcquisition")}`}
                  {activeVehicle.isEvent && ` · ${t("modal.eventExclusive")}`}
                  
                  {/* نمایش وضعیت لایو بودن دیتا */}
                  {liveVehicle && (
                    <motion.span 
                      initial={{ opacity: 0 }} animate={{ opacity: 1 }} 
                      className="ms-2 inline-flex h-1.5 w-1.5 rounded-full bg-green-500 shadow-[0_0_6px_#22c55e]"
                      title="Live Sync Active"
                    />
                  )}
                </p>
                <motion.h2 
                  layout="position"
                  className="mt-1 text-start font-display text-2xl tracking-wide text-parchment sm:text-3xl"
                >
                  {displayName}
                  {translation.isFetching && (
                    <motion.span 
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ repeat: Infinity, duration: 1.5 }}
                      className="ms-2 align-middle font-mono text-[10px] normal-case tracking-normal text-brass/70"
                    >
                      {t("language.translating")}
                    </motion.span>
                  )}
                </motion.h2>
                {translation.isError && (
                  <p className="mt-0.5 font-mono text-[10px] text-redact">
                    {t("language.translateError")}
                  </p>
                )}
              </div>
            </motion.div>

            <motion.div 
              variants={staggerContainer}
              initial="hidden"
              animate="show"
              className="grid grid-cols-3 divide-x divide-hairline border-b border-hairline"
            >
              <BrStat label={t("modal.arcade")} value={activeVehicle.br.ab} />
              <BrStat label={t("modal.realistic")} value={activeVehicle.br.rb} />
              <BrStat label={t("modal.simulator")} value={activeVehicle.br.sb} />
            </motion.div>

            <motion.div 
              variants={staggerContainer}
              initial="hidden"
              animate="show"
              className="flex flex-wrap gap-x-6 gap-y-1 border-b border-hairline px-4 py-2.5 font-mono text-[11px] text-parchment/50"
            >
              <motion.span variants={fadeUpItem}>{t("modal.crew")} {activeVehicle.crew}</motion.span>
              {activeVehicle.repairCost && (
                <motion.span variants={fadeUpItem}>{t("modal.repairRb", { value: activeVehicle.repairCost.rb.toLocaleString() })}</motion.span>
              )}
              {activeVehicle.slMultiplier !== undefined && (
                <motion.span variants={fadeUpItem}>{t("modal.slMultiplier", { value: activeVehicle.slMultiplier.toFixed(2) })}</motion.span>
              )}
              {activeVehicle.rpMultiplier !== undefined && (
                <motion.span variants={fadeUpItem}>{t("modal.rpMultiplier", { value: activeVehicle.rpMultiplier.toFixed(2) })}</motion.span>
              )}
            </motion.div>

            <div className="max-h-[50vh] overflow-y-auto overflow-x-hidden p-1">
              <AnimatePresence mode="popLayout">
                {activeVehicle.mobility && (
                  <CollapsibleSection key="mobility" title={t("modal.sectionMobility")} eyebrow={t("modal.secA")} defaultOpen>
                    <motion.dl variants={staggerContainer} initial="hidden" animate="show" className="grid grid-cols-2 gap-x-4 gap-y-2 font-mono text-xs sm:grid-cols-3">
                      {activeVehicle.mobility.enginePowerHp !== undefined && (
                        <Stat label={t("modal.power")} value={`${activeVehicle.mobility.enginePowerHp} hp`} />
                      )}
                      <Stat label={t("modal.weight")} value={`${activeVehicle.mobility.weightTons.toFixed(1)} t`} />
                      {activeVehicle.mobility.powerToWeight !== undefined && (
                        <Stat label={t("modal.powerToWeight")} value={`${activeVehicle.mobility.powerToWeight.toFixed(1)} hp/t`} />
                      )}
                      {activeVehicle.mobility.topSpeedKmh !== undefined && (
                        <Stat label={t("modal.topSpeed")} value={`${activeVehicle.mobility.topSpeedKmh} km/h`} />
                      )}
                      {activeVehicle.mobility.reverseSpeedKmh !== undefined && (
                        <Stat label={t("modal.reverse")} value={`${activeVehicle.mobility.reverseSpeedKmh} km/h`} />
                      )}
                      {activeVehicle.mobility.turnTimeSec !== undefined && (
                        <Stat label={t("modal.turnTime")} value={`${activeVehicle.mobility.turnTimeSec}s`} />
                      )}
                      {activeVehicle.mobility.climbRateMs !== undefined && (
                        <Stat label={t("modal.climb")} value={`${activeVehicle.mobility.climbRateMs} m/s`} />
                      )}
                      {activeVehicle.mobility.transmission && (
                        <Stat label={t("modal.transmission")} value={activeVehicle.mobility.transmission} />
                      )}
                    </motion.dl>
                  </CollapsibleSection>
                )}

                {activeVehicle.firepower && (
                  <CollapsibleSection key="firepower" title={t("modal.sectionFirepower")} eyebrow={t("modal.secB")}>
                    <motion.div variants={staggerContainer} initial="hidden" animate="show" className="flex flex-wrap gap-x-4 gap-y-2 font-mono text-xs">
                      <Stat label={t("modal.reloadBase")} value={`${activeVehicle.firepower.reloadBaseSec}s`} />
                      <Stat label={t("modal.reloadAced")} value={`${activeVehicle.firepower.reloadAcedSec}s`} />
                      {activeVehicle.firepower.verticalTargetingSpeedDegS !== undefined && (
                        <Stat label={t("modal.vertTraverse")} value={`${activeVehicle.firepower.verticalTargetingSpeedDegS}°/s`} />
                      )}
                      {activeVehicle.firepower.horizontalTargetingSpeedDegS !== undefined && (
                        <Stat label={t("modal.horizTraverse")} value={`${activeVehicle.firepower.horizontalTargetingSpeedDegS}°/s`} />
                      )}
                    </motion.div>

                    <motion.div variants={staggerContainer} initial="hidden" animate="show" className="mt-3 space-y-3">
                      {activeVehicle.firepower.ammoTypes.map((round) => (
                        <motion.div variants={fadeUpItem} key={round.name} className="border border-hairline p-2.5 transition-colors hover:bg-white/[0.02]">
                          <div className="flex items-baseline justify-between">
                            <p className="text-start font-body text-sm text-parchment">
                              {round.name}{" "}
                              <span className="font-mono text-[10px] text-parchment/40">{round.type}</span>
                            </p>
                            <p className="font-mono text-[10px] text-parchment/50">
                              <bdi dir="ltr">{round.muzzleVelocityMs} m/s</bdi>
                            </p>
                          </div>
                          {round.penetration.length > 0 && (
                            <table className="mt-2 w-full font-mono text-[10px] text-parchment/70">
                              <thead>
                                <tr className="text-start text-parchment/40">
                                  <th className="font-normal">Range</th>
                                  <th className="font-normal">0°</th>
                                  <th className="font-normal">30°</th>
                                  <th className="font-normal">60°</th>
                                </tr>
                              </thead>
                              <tbody>
                                {round.penetration.map((p) => (
                                  <tr key={p.rangeM} className="transition-colors hover:text-brass">
                                    <td className="py-0.5"><bdi dir="ltr">{p.rangeM}m</bdi></td>
                                    <td><bdi dir="ltr">{p.angle0}</bdi></td>
                                    <td><bdi dir="ltr">{p.angle30}</bdi></td>
                                    <td><bdi dir="ltr">{p.angle60}</bdi></td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          )}
                        </motion.div>
                      ))}
                    </motion.div>
                  </CollapsibleSection>
                )}

                {activeVehicle.armor && (
                  <CollapsibleSection key="armor" title={t("modal.sectionArmor")} eyebrow={t("modal.secC")}>
                    <motion.dl variants={staggerContainer} initial="hidden" animate="show" className="grid grid-cols-2 gap-x-4 gap-y-2 font-mono text-xs sm:grid-cols-3">
                      <Stat label={t("modal.hullFront")} value={`${activeVehicle.armor.hullFrontMm} mm`} />
                      <Stat label={t("modal.hullSide")} value={`${activeVehicle.armor.hullSideMm} mm`} />
                      <Stat label={t("modal.hullRear")} value={`${activeVehicle.armor.hullRearMm} mm`} />
                      {activeVehicle.armor.turretFrontMm !== undefined && (
                        <Stat label={t("modal.turretFront")} value={`${activeVehicle.armor.turretFrontMm} mm`} />
                      )}
                      {activeVehicle.armor.turretSideMm !== undefined && (
                        <Stat label={t("modal.turretSide")} value={`${activeVehicle.armor.turretSideMm} mm`} />
                      )}
                      {activeVehicle.armor.turretRearMm !== undefined && (
                        <Stat label={t("modal.turretRear")} value={`${activeVehicle.armor.turretRearMm} mm`} />
                      )}
                      <Stat label={t("modal.era")} value={activeVehicle.armor.era ? t("modal.fitted") : t("modal.none")} />
                      <Stat label={t("modal.composite")} value={activeVehicle.armor.composite ? t("modal.yes") : t("modal.no")} />
                    </motion.dl>
                    {displayModuleNotes && (
                      <motion.p variants={fadeUpItem} className="mt-2 text-start font-body text-xs leading-relaxed text-parchment/60">
                        {displayModuleNotes}
                      </motion.p>
                    )}
                  </CollapsibleSection>
                )}

                {activeVehicle.avionics && (
                  <CollapsibleSection key="avionics" title={t("modal.sectionAvionics")} eyebrow={t("modal.secD")}>
                    <motion.dl variants={staggerContainer} initial="hidden" animate="show" className="grid grid-cols-2 gap-x-4 gap-y-2 font-mono text-xs sm:grid-cols-3">
                      {activeVehicle.avionics.radarRangeKm !== undefined && (
                        <Stat label={t("modal.radarRange")} value={`${activeVehicle.avionics.radarRangeKm} km`} />
                      )}
                      {activeVehicle.avionics.thermalGen !== undefined && (
                        <Stat label={t("modal.thermal")} value={t("modal.genN", { n: activeVehicle.avionics.thermalGen })} />
                      )}
                      <Stat label={t("modal.rwr")} value={activeVehicle.avionics.rwr ? t("modal.fitted") : t("modal.none")} />
                      <Stat label={t("modal.laserWarning")} value={activeVehicle.avionics.lwr ? t("modal.fitted") : t("modal.none")} />
                      <Stat label={t("modal.ballisticComputer")} value={activeVehicle.avionics.ballisticComputer ? t("modal.yes") : t("modal.no")} />
                    </motion.dl>
                  </CollapsibleSection>
                )}

                <CollapsibleSection key="protips" title={t("modal.sectionProTips")} eyebrow={t("modal.fieldNotes")}>
                  <motion.ul variants={staggerContainer} initial="hidden" animate="show" className="list-inside list-disc space-y-1.5 text-start font-body text-sm leading-snug text-parchment/75">
                    {displayProTips.map((tip, i) => (
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

function BrStat({ label, value }: { label: string; value: number }) {
  return (
    <motion.div variants={fadeUpItem} className="px-3 py-2.5 text-center">
      <p className="font-mono text-[9px] uppercase tracking-widest2 text-parchment/40">{label}</p>
      {/* تغییر رنگ لحظه‌ای در صورت آپدیت مقدار با انیمیشن */}
      <motion.p 
        key={value}
        initial={{ scale: 1.2, color: "#fff" }}
        animate={{ scale: 1, color: "var(--brass, #eab308)" }}
        className="font-mono text-lg"
      >
        <bdi dir="ltr">{value.toFixed(1)}</bdi>
      </motion.p>
    </motion.div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <motion.div variants={fadeUpItem} layout className="group">
      <dt className="text-parchment/40 transition-colors group-hover:text-parchment/60">{label}</dt>
      <motion.dd 
        key={value}
        initial={{ opacity: 0.5, x: -5 }}
        animate={{ opacity: 1, x: 0 }}
        className="text-parchment transition-colors group-hover:text-brass"
      >
        <bdi dir="ltr">{value}</bdi>
      </motion.dd>
    </motion.div>
  );
}
