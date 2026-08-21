"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useTranslations } from "next-intl";
import clsx from "clsx";
import type { Vehicle } from "@/lib/types";

export function VehicleCard({
  vehicle,
  onOpen,
}: {
  vehicle: Vehicle;
  onOpen: (v: Vehicle) => void;
}) {
  const t = useTranslations();
  // FIX: the card used to always render the decorative gradient plate,
  // even when a real vehicle.imageUrl was available — the scraper had
  // been collecting image URLs all along, but nothing on the frontend
  // ever displayed them. imageFailed tracks a broken/missing image so
  // the card falls back to the same decorative plate instead of showing
  // a broken-image icon.
  const [imageFailed, setImageFailed] = useState(false);
  const hasImage = Boolean(vehicle.imageUrl) && !imageFailed;

  return (
    <motion.button
      layoutId={`card-${vehicle.id}`}
      onClick={() => onOpen(vehicle)}
      className="group flex h-full flex-col overflow-hidden rounded-sm border border-hairline bg-panel text-start transition-colors hover:border-brass/60 focus-visible:border-brass"
    >
      <motion.div
        layoutId={`card-plate-${vehicle.id}`}
        className="relative h-24 w-full shrink-0 overflow-hidden bg-gradient-to-br from-panel2 to-ink"
      >
        {hasImage ? (
          // Hotlinked directly from Gaijin's own official asset CDN — the
          // image is served straight from their servers to the browser,
          // never downloaded or re-hosted by this project. Same practice
          // as any fan wiki/reference site linking official icons.
          <img
            src={vehicle.imageUrl}
            alt={vehicle.name}
            loading="lazy"
            onError={() => setImageFailed(true)}
            className="absolute inset-0 h-full w-full object-contain p-1.5 transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="absolute inset-0 opacity-[0.08] [background-image:repeating-linear-gradient(115deg,transparent,transparent_10px,#E8E4D6_10px,#E8E4D6_11px)]" />
        )}
        {/* gradient wash so the badges/rank label stay readable over a photo */}
        {hasImage && (
          <div className="absolute inset-0 bg-gradient-to-t from-ink/70 via-transparent to-transparent" />
        )}
        <div className="absolute start-2 top-2 h-1.5 w-1.5 rounded-full bg-hairline" />
        <div className="absolute flex gap-1 end-2 top-2">
          {vehicle.isPremium && <Badge tone="brass">PREM</Badge>}
          {vehicle.isEvent && <Badge tone="parchment">EVENT</Badge>}
          {vehicle.isRare && <Badge tone="redact">RARE</Badge>}
        </div>
        <span className="absolute bottom-1.5 start-2 font-mono text-[10px] uppercase tracking-widest2 text-parchment/40">
          <bdi dir="ltr">Rk {vehicle.rank}</bdi>
        </span>
      </motion.div>

      <div className="flex flex-1 flex-col gap-1 p-2.5">
        <p className="line-clamp-2 text-start font-body text-[13px] font-medium leading-tight text-parchment">
          {vehicle.name}
        </p>
        <div className="mt-auto flex items-center justify-between pt-1">
          <span className="font-mono text-[10px] text-parchment/40">
            <bdi dir="ltr">{vehicle.crew}★</bdi> {t("modal.crew")}
          </span>
          <span className="font-mono text-xs font-medium text-brass">
            <bdi dir="ltr">{vehicle.br.rb.toFixed(1)}</bdi>
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
