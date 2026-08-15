"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { Vehicle } from "@/lib/types";
import { NATION_LABELS } from "@/lib/types";
import { CollapsibleSection } from "./CollapsibleSection";

export function VehicleModal({
  vehicle,
  onClose,
}: {
  vehicle: Vehicle | null;
  onClose: () => void;
}) {
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
          aria-label={vehicle.name}
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
                aria-label="Close dossier"
                className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-sm border border-hairline bg-ink/60 font-mono text-parchment/70 transition-colors hover:border-brass hover:text-brass"
              >
                ✕
              </button>
              <div className="absolute bottom-3 left-4 right-4">
                <p className="font-mono text-[10px] uppercase tracking-widest2 text-brass">
                  {NATION_LABELS[vehicle.nation]} · Rank {vehicle.rank}
                  {vehicle.isRare && " · Rare acquisition"}
                  {vehicle.isEvent && " · Event exclusive"}
                </p>
                <h2 className="mt-1 font-display text-2xl tracking-wide text-parchment sm:text-3xl">
                  {vehicle.name}
                </h2>
              </div>
            </motion.div>

            <div className="grid grid-cols-3 divide-x divide-hairline border-b border-hairline">
              <BrStat label="Arcade" value={vehicle.br.ab} />
              <BrStat label="Realistic" value={vehicle.br.rb} />
              <BrStat label="Simulator" value={vehicle.br.sb} />
            </div>

            <div className="flex flex-wrap gap-x-6 gap-y-1 border-b border-hairline px-4 py-2.5 font-mono text-[11px] text-parchment/50">
              <span>Crew {vehicle.crew}</span>
              <span>
                Repair {vehicle.repairCost.rb.toLocaleString()} SL (RB)
              </span>
              <span>SL ×{vehicle.slMultiplier.toFixed(2)}</span>
              <span>RP ×{vehicle.rpMultiplier.toFixed(2)}</span>
            </div>

            <div className="max-h-[50vh] overflow-y-auto">
              {vehicle.mobility && (
                <CollapsibleSection title="Mobility" eyebrow="Sec. A" defaultOpen>
                  <dl className="grid grid-cols-2 gap-x-4 gap-y-2 font-mono text-xs sm:grid-cols-3">
                    <Stat label="Power" value={`${vehicle.mobility.enginePowerHp} hp`} />
                    <Stat label="Weight" value={`${vehicle.mobility.weightTons.toFixed(1)} t`} />
                    <Stat
                      label="Power/wt"
                      value={`${vehicle.mobility.powerToWeight.toFixed(1)} hp/t`}
                    />
                    <Stat label="Top speed" value={`${vehicle.mobility.topSpeedKmh} km/h`} />
                    {vehicle.mobility.reverseSpeedKmh !== undefined && (
                      <Stat
                        label="Reverse"
                        value={`${vehicle.mobility.reverseSpeedKmh} km/h`}
                      />
                    )}
                    {vehicle.mobility.turnTimeSec !== undefined && (
                      <Stat label="Turn time" value={`${vehicle.mobility.turnTimeSec}s`} />
                    )}
                    {vehicle.mobility.climbRateMs !== undefined && (
                      <Stat label="Climb" value={`${vehicle.mobility.climbRateMs} m/s`} />
                    )}
                    {vehicle.mobility.transmission && (
                      <Stat label="Transmission" value={vehicle.mobility.transmission} />
                    )}
                  </dl>
                </CollapsibleSection>
              )}

              {vehicle.firepower && (
                <CollapsibleSection title="Firepower" eyebrow="Sec. B">
                  <div className="flex flex-wrap gap-x-4 gap-y-2 font-mono text-xs">
                    <Stat label="Reload (base)" value={`${vehicle.firepower.reloadBaseSec}s`} />
                    <Stat label="Reload (aced)" value={`${vehicle.firepower.reloadAcedSec}s`} />
                    {vehicle.firepower.verticalTargetingSpeedDegS !== undefined && (
                      <Stat
                        label="Vert. traverse"
                        value={`${vehicle.firepower.verticalTargetingSpeedDegS}°/s`}
                      />
                    )}
                    {vehicle.firepower.horizontalTargetingSpeedDegS !== undefined && (
                      <Stat
                        label="Horiz. traverse"
                        value={`${vehicle.firepower.horizontalTargetingSpeedDegS}°/s`}
                      />
                    )}
                  </div>

                  <div className="mt-3 space-y-3">
                    {vehicle.firepower.ammoTypes.map((round) => (
                      <div key={round.name} className="border border-hairline p-2.5">
                        <div className="flex items-baseline justify-between">
                          <p className="font-body text-sm text-parchment">
                            {round.name}{" "}
                            <span className="font-mono text-[10px] text-parchment/40">
                              {round.type}
                            </span>
                          </p>
                          <p className="font-mono text-[10px] text-parchment/50">
                            {round.muzzleVelocityMs} m/s
                          </p>
                        </div>
                        {round.penetration.length > 0 && (
                          <table className="mt-2 w-full font-mono text-[10px] text-parchment/70">
                            <thead>
                              <tr className="text-left text-parchment/40">
                                <th className="font-normal">Range</th>
                                <th className="font-normal">0°</th>
                                <th className="font-normal">30°</th>
                                <th className="font-normal">60°</th>
                              </tr>
                            </thead>
                            <tbody>
                              {round.penetration.map((p) => (
                                <tr key={p.rangeM}>
                                  <td className="py-0.5">{p.rangeM}m</td>
                                  <td>{p.angle0}</td>
                                  <td>{p.angle30}</td>
                                  <td>{p.angle60}</td>
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
                <CollapsibleSection title="Armor & survivability" eyebrow="Sec. C">
                  <dl className="grid grid-cols-2 gap-x-4 gap-y-2 font-mono text-xs sm:grid-cols-3">
                    <Stat label="Hull front" value={`${vehicle.armor.hullFrontMm} mm`} />
                    <Stat label="Hull side" value={`${vehicle.armor.hullSideMm} mm`} />
                    <Stat label="Hull rear" value={`${vehicle.armor.hullRearMm} mm`} />
                    {vehicle.armor.turretFrontMm !== undefined && (
                      <Stat label="Turret front" value={`${vehicle.armor.turretFrontMm} mm`} />
                    )}
                    {vehicle.armor.turretSideMm !== undefined && (
                      <Stat label="Turret side" value={`${vehicle.armor.turretSideMm} mm`} />
                    )}
                    {vehicle.armor.turretRearMm !== undefined && (
                      <Stat label="Turret rear" value={`${vehicle.armor.turretRearMm} mm`} />
                    )}
                    <Stat label="ERA" value={vehicle.armor.era ? "Fitted" : "None"} />
                    <Stat label="Composite" value={vehicle.armor.composite ? "Yes" : "No"} />
                  </dl>
                  {vehicle.armor.moduleNotes && (
                    <p className="mt-2 font-body text-xs leading-relaxed text-parchment/60">
                      {vehicle.armor.moduleNotes}
                    </p>
                  )}
                </CollapsibleSection>
              )}

              {vehicle.avionics && (
                <CollapsibleSection title="Avionics" eyebrow="Sec. D">
                  <dl className="grid grid-cols-2 gap-x-4 gap-y-2 font-mono text-xs sm:grid-cols-3">
                    {vehicle.avionics.radarRangeKm !== undefined && (
                      <Stat label="Radar range" value={`${vehicle.avionics.radarRangeKm} km`} />
                    )}
                    {vehicle.avionics.thermalGen !== undefined && (
                      <Stat label="Thermal" value={`Gen ${vehicle.avionics.thermalGen}`} />
                    )}
                    <Stat label="RWR" value={vehicle.avionics.rwr ? "Fitted" : "None"} />
                    <Stat label="Laser warning" value={vehicle.avionics.lwr ? "Fitted" : "None"} />
                    <Stat
                      label="Ballistic computer"
                      value={vehicle.avionics.ballisticComputer ? "Yes" : "No"}
                    />
                  </dl>
                </CollapsibleSection>
              )}

              <CollapsibleSection title="Pro player tips" eyebrow="Field notes">
                <ul className="list-inside list-disc space-y-1.5 font-body text-sm leading-snug text-parchment/75">
                  {vehicle.proTips.map((tip, i) => (
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
      <p className="font-mono text-[9px] uppercase tracking-widest2 text-parchment/40">
        {label}
      </p>
      <p className="font-mono text-lg text-brass">{value.toFixed(1)}</p>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-parchment/40">{label}</dt>
      <dd className="text-parchment">{value}</dd>
    </div>
  );
}
