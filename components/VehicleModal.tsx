"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useTranslations } from "next-intl";
import type { Vehicle } from "@/lib/types";
import { useTranslatedVehicle } from "@/hooks/useTranslatedVehicle";
import { CollapsibleSection } from "./CollapsibleSection";

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

  const displayName = translation.data?.name ?? vehicle?.name;
  const displayProTips = translation.data?.proTips ?? vehicle?.proTips ?? [];
  const displayModuleNotes = translation.data?.moduleNotes ?? vehicle?.armor?.moduleNotes;

  return (
    <AnimatePresence>
      {vehicle && (
        <motion.div
          className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-ink/80 p-4 py-10 backdrop-blur-sm sm:items-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          role="dialog"
          aria-modal="true"
          aria-label={displayName}
        >
          <motion.div
            layoutId={`card-${vehicle.id}`}
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-2xl overflow-hidden rounded-sm border border-hairline bg-panel shadow-dossier"
          >
            <motion.div
              layoutId={`card-plate-${vehicle.id}`}
              className="relative h-36 w-full bg-gradient-to-br from-panel2 to-ink sm:h-44"
            >
              <div className="absolute inset-0 opacity-[0.08] [background-image:repeating-linear-gradient(115deg,transparent,transparent_10px,#E8E4D6_10px,#E8E4D6_11px)]" />
              <button
                type="button"
                onClick={onClose}
                aria-label={t("modal.close")}
                className="absolute end-3 top-3 flex h-8 w-8 items-center justify-center rounded-sm border border-hairline bg-ink/60 font-mono text-parchment/70 transition-colors hover:border-brass hover:text-brass"
              >
                ✕
              </button>
              <div className="absolute bottom-3 start-4 end-4">
                <p className="font-mono text-[10px] uppercase tracking-widest2 text-brass">
                  {t(`nation.${vehicle.nation}`)} · Rk {vehicle.rank}
                  {vehicle.isRare && ` · ${t("modal.rareAcquisition")}`}
                  {vehicle.isEvent && ` · ${t("modal.eventExclusive")}`}
                </p>
                <h2 className="mt-1 text-start font-display text-2xl tracking-wide text-parchment sm:text-3xl">
                  {displayName}
                  {translation.isFetching && (
                    <span className="ms-2 align-middle font-mono text-[10px] normal-case tracking-normal text-brass/70">
                      {t("language.translating")}
                    </span>
                  )}
                </h2>
                {translation.isError && (
                  <p className="mt-0.5 font-mono text-[10px] text-redact">
                    {t("language.translateError")}
                  </p>
                )}
              </div>
            </motion.div>

            <div className="grid grid-cols-3 divide-x divide-hairline border-b border-hairline">
              <BrStat label={t("modal.arcade")} value={vehicle.br.ab} />
              <BrStat label={t("modal.realistic")} value={vehicle.br.rb} />
              <BrStat label={t("modal.simulator")} value={vehicle.br.sb} />
            </div>

            <div className="flex flex-wrap gap-x-6 gap-y-1 border-b border-hairline px-4 py-2.5 font-mono text-[11px] text-parchment/50">
              <span>{t("modal.crew")} {vehicle.crew}</span>
              {vehicle.repairCost && (
                <span>{t("modal.repairRb", { value: vehicle.repairCost.rb.toLocaleString() })}</span>
              )}
              {vehicle.slMultiplier !== undefined && (
                <span>{t("modal.slMultiplier", { value: vehicle.slMultiplier.toFixed(2) })}</span>
              )}
              {vehicle.rpMultiplier !== undefined && (
                <span>{t("modal.rpMultiplier", { value: vehicle.rpMultiplier.toFixed(2) })}</span>
              )}
            </div>

            <div className="max-h-[50vh] overflow-y-auto">
              {vehicle.mobility && (
                <CollapsibleSection title={t("modal.sectionMobility")} eyebrow={t("modal.secA")} defaultOpen>
                  <dl className="grid grid-cols-2 gap-x-4 gap-y-2 font-mono text-xs sm:grid-cols-3">
                    {vehicle.mobility.enginePowerHp !== undefined && (
                      <Stat label={t("modal.power")} value={`${vehicle.mobility.enginePowerHp} hp`} />
                    )}
                    <Stat label={t("modal.weight")} value={`${vehicle.mobility.weightTons.toFixed(1)} t`} />
                    {vehicle.mobility.powerToWeight !== undefined && (
                      <Stat label={t("modal.powerToWeight")} value={`${vehicle.mobility.powerToWeight.toFixed(1)} hp/t`} />
                    )}
                    {vehicle.mobility.topSpeedKmh !== undefined && (
                      <Stat label={t("modal.topSpeed")} value={`${vehicle.mobility.topSpeedKmh} km/h`} />
                    )}
                    {vehicle.mobility.reverseSpeedKmh !== undefined && (
                      <Stat label={t("modal.reverse")} value={`${vehicle.mobility.reverseSpeedKmh} km/h`} />
                    )}
                    {vehicle.mobility.turnTimeSec !== undefined && (
                      <Stat label={t("modal.turnTime")} value={`${vehicle.mobility.turnTimeSec}s`} />
                    )}
                    {vehicle.mobility.climbRateMs !== undefined && (
                      <Stat label={t("modal.climb")} value={`${vehicle.mobility.climbRateMs} m/s`} />
                    )}
                    {vehicle.mobility.transmission && (
                      <Stat label={t("modal.transmission")} value={vehicle.mobility.transmission} />
                    )}
                  </dl>
                </CollapsibleSection>
              )}

              {vehicle.firepower && (
                <CollapsibleSection title={t("modal.sectionFirepower")} eyebrow={t("modal.secB")}>
                  <div className="flex flex-wrap gap-x-4 gap-y-2 font-mono text-xs">
                    <Stat label={t("modal.reloadBase")} value={`${vehicle.firepower.reloadBaseSec}s`} />
                    <Stat label={t("modal.reloadAced")} value={`${vehicle.firepower.reloadAcedSec}s`} />
                    {vehicle.firepower.verticalTargetingSpeedDegS !== undefined && (
                      <Stat label={t("modal.vertTraverse")} value={`${vehicle.firepower.verticalTargetingSpeedDegS}°/s`} />
                    )}
                    {vehicle.firepower.horizontalTargetingSpeedDegS !== undefined && (
                      <Stat label={t("modal.horizTraverse")} value={`${vehicle.firepower.horizontalTargetingSpeedDegS}°/s`} />
                    )}
                  </div>

                  <div className="mt-3 space-y-3">
                    {vehicle.firepower.ammoTypes.map((round) => (
                      <div key={round.name} className="border border-hairline p-2.5">
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
                                <tr key={p.rangeM}>
                                  <td className="py-0.5"><bdi dir="ltr">{p.rangeM}m</bdi></td>
                                  <td><bdi dir="ltr">{p.angle0}</bdi></td>
                                  <td><bdi dir="ltr">{p.angle30}</bdi></td>
                                  <td><bdi dir="ltr">{p.angle60}</bdi></td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        )}
                      </div>
                    ))}
                  </div>
                </CollapsibleSection>
              )}

              {vehicle.armor && (
                <CollapsibleSection title={t("modal.sectionArmor")} eyebrow={t("modal.secC")}>
                  <dl className="grid grid-cols-2 gap-x-4 gap-y-2 font-mono text-xs sm:grid-cols-3">
                    <Stat label={t("modal.hullFront")} value={`${vehicle.armor.hullFrontMm} mm`} />
                    <Stat label={t("modal.hullSide")} value={`${vehicle.armor.hullSideMm} mm`} />
                    <Stat label={t("modal.hullRear")} value={`${vehicle.armor.hullRearMm} mm`} />
                    {vehicle.armor.turretFrontMm !== undefined && (
                      <Stat label={t("modal.turretFront")} value={`${vehicle.armor.turretFrontMm} mm`} />
                    )}
                    {vehicle.armor.turretSideMm !== undefined && (
                      <Stat label={t("modal.turretSide")} value={`${vehicle.armor.turretSideMm} mm`} />
                    )}
                    {vehicle.armor.turretRearMm !== undefined && (
                      <Stat label={t("modal.turretRear")} value={`${vehicle.armor.turretRearMm} mm`} />
                    )}
                    <Stat label={t("modal.era")} value={vehicle.armor.era ? t("modal.fitted") : t("modal.none")} />
                    <Stat label={t("modal.composite")} value={vehicle.armor.composite ? t("modal.yes") : t("modal.no")} />
                  </dl>
                  {displayModuleNotes && (
                    <p className="mt-2 text-start font-body text-xs leading-relaxed text-parchment/60">
                      {displayModuleNotes}
                    </p>
                  )}
                </CollapsibleSection>
              )}

              {vehicle.avionics && (
                <CollapsibleSection title={t("modal.sectionAvionics")} eyebrow={t("modal.secD")}>
                  <dl className="grid grid-cols-2 gap-x-4 gap-y-2 font-mono text-xs sm:grid-cols-3">
                    {vehicle.avionics.radarRangeKm !== undefined && (
                      <Stat label={t("modal.radarRange")} value={`${vehicle.avionics.radarRangeKm} km`} />
                    )}
                    {vehicle.avionics.thermalGen !== undefined && (
                      <Stat label={t("modal.thermal")} value={t("modal.genN", { n: vehicle.avionics.thermalGen })} />
                    )}
                    <Stat label={t("modal.rwr")} value={vehicle.avionics.rwr ? t("modal.fitted") : t("modal.none")} />
                    <Stat label={t("modal.laserWarning")} value={vehicle.avionics.lwr ? t("modal.fitted") : t("modal.none")} />
                    <Stat label={t("modal.ballisticComputer")} value={vehicle.avionics.ballisticComputer ? t("modal.yes") : t("modal.no")} />
                  </dl>
                </CollapsibleSection>
              )}

              <CollapsibleSection title={t("modal.sectionProTips")} eyebrow={t("modal.fieldNotes")}>
                <ul className="list-inside list-disc space-y-1.5 text-start font-body text-sm leading-snug text-parchment/75">
                  {displayProTips.map((tip, i) => (
                    <li key={i}>{tip}</li>
                  ))}
                </ul>
              </CollapsibleSection>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
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

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-parchment/40">{label}</dt>
      <dd className="text-parchment">
        <bdi dir="ltr">{value}</bdi>
      </dd>
    </div>
  );
}
