"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { useTranslations } from "next-intl";

interface Slide {
  id: string;
  eyebrowKey: string;
  titleKey: string;
  captionKey: string;
  gradient: string;
}

// Copy lives in messages/*.json (hero.eyebrow1/title1/caption1, etc) — this
// array is just which keys + which placeholder gradient go together, so it
// stays locale-independent.
const SLIDES: Slide[] = [
  { id: "combined-arms", eyebrowKey: "eyebrow1", titleKey: "title1", captionKey: "caption1",
    gradient: "from-[#12140d] via-[#1c2013] to-[#0b0c08]" },
  { id: "top-tier-air", eyebrowKey: "eyebrow2", titleKey: "title2", captionKey: "caption2",
    gradient: "from-[#0d1512] via-[#12211d] to-[#0b0c08]" },
  { id: "naval-annex", eyebrowKey: "eyebrow3", titleKey: "title3", captionKey: "caption3",
    gradient: "from-[#0d1418] via-[#131f26] to-[#0b0c08]" },
];

const SLIDE_DURATION_MS = 10_000;

export function Hero({ visible }: { visible: boolean }) {
  const t = useTranslations("hero");
  const [index, setIndex] = useState(0);
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    if (!visible) return;
    const timer = setInterval(
      () => setIndex((i) => (i + 1) % SLIDES.length),
      SLIDE_DURATION_MS
    );
    return () => clearInterval(timer);
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
          {t(slide.eyebrowKey)}
        </p>
        <h1 className="mt-3 max-w-xl text-start font-display text-3xl leading-tight tracking-wide text-parchment sm:text-5xl">
          {t(slide.titleKey)}
        </h1>
        <p className="mt-3 font-mono text-xs text-parchment/60">{t(slide.captionKey)}</p>

        <div className="mt-6 flex gap-1.5" role="tablist" aria-label="Hero slides">
          {SLIDES.map((s, i) => (
            <button
              key={s.id}
              role="tab"
              aria-selected={i === index}
              aria-label={t(s.titleKey)}
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
