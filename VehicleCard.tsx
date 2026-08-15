"use client";

import { motion } from "framer-motion";
import clsx from "clsx";
import type { Vehicle } from "@/lib/types";

export function VehicleCard({
  vehicle,
  onOpen,
}: {
  vehicle: Vehicle;
  onOpen: (v: Vehicle) => void;
}) {
  return (
    <motion.button
      layoutId={`card-${vehicle.id}`}
      onClick={() => onOpen(vehicle)}
      className="group flex h-full flex-col overflow-hidden rounded-sm border border-hairline bg-panel text-left transition-colors hover:border-brass/60 focus-visible:border-brass"
    >
      <motion.div
        layoutId={`card-plate-${vehicle.id}`}
        className="relative h-24 w-full shrink-0 bg-gradient-to-br from-panel2 to-ink"
      >
        <div className="absolute inset-0 opacity-[0.08] [background-image:repeating-linear-gradient(115deg,transparent,transparent_10px,#E8E4D6_10px,#E8E4D6_11px)]" />
        <div className="absolute left-2 top-2 h-1.5 w-1.5 rounded-full bg-hairline" />
        <div className="absolute flex gap-1 right-2 top-2">
          {vehicle.isPremium && <Badge tone="brass">PREM</Badge>}
          {vehicle.isEvent && <Badge tone="parchment">EVENT</Badge>}
          {vehicle.isRare && <Badge tone="redact">RARE</Badge>}
        </div>
        <span className="absolute bottom-1.5 left-2 font-mono text-[10px] uppercase tracking-widest2 text-parchment/40">
          Rk {vehicle.rank}
        </span>
      </motion.div>

      <div className="flex flex-1 flex-col gap-1 p-2.5">
        <p className="line-clamp-2 font-body text-[13px] font-medium leading-tight text-parchment">
          {vehicle.name}
        </p>
        <div className="mt-auto flex items-center justify-between pt-1">
          <span className="font-mono text-[10px] text-parchment/40">
            {vehicle.crew}★ crew
          </span>
          <span className="font-mono text-xs font-medium text-brass">
            {vehicle.br.rb.toFixed(1)}
          </span>
        </div>
      </div>
    </motion.button>
  );
}

function Badge({
  children,
  tone,
}: {
  children: string;
  tone: "brass" | "parchment" | "redact";
}) {
  return (
    <span
      className={clsx(
        "rounded-[2px] px-1 py-0.5 font-mono text-[9px] font-semibold tracking-wide",
        tone === "brass" && "bg-brass text-ink",
        tone === "parchment" && "bg-parchment text-ink",
        tone === "redact" && "bg-redact text-parchment"
      )}
    >
      {children}
    </span>
  );
}
