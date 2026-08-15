"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";

export interface HeroSlide {
  id: string;
  eyebrow: string;
  title: string;
  caption: string;
  // Optional real screenshot URL. Leave undefined to use the generated
  // dossier-plate placeholder (see README "Hero imagery" for why the
  // default ships without real game screenshots).
  imageUrl?: string;
  gradient: string; // tailwind gradient classes for the placeholder plate
}

const SLIDES: HeroSlide[] = [
  {
    id: "combined-arms",
    eyebrow: "Field Dossier · Combined Arms",
    title: "Every hull, airframe & hull number — catalogued.",
    caption: "2,600+ records indexed across ten nations.",
    gradient: "from-[#12140d] via-[#1c2013] to-[#0b0c08]",
  },
  {
    id: "top-tier-air",
    eyebrow: "Clearance Level · Top Tier",
    title: "Rank VIII airframes, decoded to the avionics suite.",
    caption: "Radar bands, thermal generation, RWR — on file.",
    gradient: "from-[#0d1512] via-[#12211d] to-[#0b0c08]",
  },
  {
    id: "naval-annex",
    eyebrow: "Annex C · Fleet",
    title: "Coastal patrol to blue-water — every hull class.",
    caption: "Displacement, belt armor, AA suites cross-referenced.",
    gradient: "from-[#0d1418] via-[#131f26] to-[#0b0c08]",
  },
];

const SLIDE_DURATION_MS = 10_000;

export function Hero({ visible }: { visible: boolean }) {
  const [index, setIndex] = useState(0);
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    if (!visible) return;
    const t = setInterval(
      () => setIndex((i) => (i + 1) % SLIDES.length),
      SLIDE_DURATION_MS
    );
    return () => clearInterval(t);
  }, [visible]);

  if (!visible) return null;

  const slide = SLIDES[index];

  return (
    <div className="relative h-[56vh] min-h-[360px] w-full overflow-hidden border-b border-hairline">
      <AnimatePresence mode="sync">
        <motion.div
          key={slide.id}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1.1, ease: "easeInOut" }}
          className="absolute inset-0"
        >
          <motion.div
            initial={{ scale: 1 }}
            animate={{ scale: reduceMotion ? 1 : 1.08 }}
            transition={{ duration: SLIDE_DURATION_MS / 1000, ease: "linear" }}
            className={`h-full w-full bg-gradient-to-br ${slide.gradient}`}
          >
            {/* redacted-bar texture, stands in for a real screenshot plate */}
            <div className="absolute inset-0 opacity-[0.07] [background-image:repeating-linear-gradient(115deg,transparent,transparent_38px,#E8E4D6_38px,#E8E4D6_40px)]" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_30%_20%,rgba(199,160,70,0.10),transparent_55%)]" />
          </motion.div>
        </motion.div>
      </AnimatePresence>

      <div className="relative z-10 flex h-full flex-col justify-end p-6 sm:p-10">
        <p className="font-mono text-[11px] uppercase tracking-widest2 text-brass">
          {slide.eyebrow}
        </p>
        <h1 className="mt-3 max-w-xl font-display text-3xl leading-tight tracking-wide text-parchment sm:text-5xl">
          {slide.title}
        </h1>
        <p className="mt-3 font-mono text-xs text-parchment/60">{slide.caption}</p>

        <div className="mt-6 flex gap-1.5" role="tablist" aria-label="Hero slides">
          {SLIDES.map((s, i) => (
            <button
              key={s.id}
              role="tab"
              aria-selected={i === index}
              aria-label={`Show slide ${i + 1}: ${s.title}`}
              onClick={() => setIndex(i)}
              className={`h-1 rounded-full transition-all ${
                i === index ? "w-8 bg-brass" : "w-4 bg-parchment/20 hover:bg-parchment/40"
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
