"use client";

import { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import clsx from "clsx";
import { NATIONS, CATEGORIES } from "@/lib/taxonomy";
import type { Category, Nation } from "@/lib/types";

export function Sidebar({
  onSelect,
  activeSelection,
}: {
  onSelect: (nation: Nation, category: Category) => void;
  activeSelection: { nation: Nation; category: Category } | null;
}) {
  const [openNation, setOpenNation] = useState<Nation | null>(null);
  const reduceMotion = useReducedMotion();

  const close = () => setOpenNation(null);

  return (
    // eslint-disable-next-line jsx-a11y/no-noninteractive-element-interactions
    <nav
      aria-label="Nation and vehicle category"
      className="relative z-30 flex h-full shrink-0"
      onMouseLeave={close}
    >
      <ul className="flex w-16 flex-col border-r border-hairline bg-panel py-3 sm:w-[72px]">
        {NATIONS.map((nation) => {
          const isOpen = openNation === nation.id;
          const isActive = activeSelection?.nation === nation.id;
          return (
            <li key={nation.id}>
              <button
                type="button"
                onMouseEnter={() => setOpenNation(nation.id)}
                onFocus={() => setOpenNation(nation.id)}
                onClick={() =>
                  setOpenNation((prev) => (prev === nation.id ? null : nation.id))
                }
                aria-haspopup="true"
                aria-expanded={isOpen}
                className={clsx(
                  "tab-cut group relative flex h-[52px] w-full items-center justify-center border-l-2 transition-colors",
                  isOpen || isActive
                    ? "border-brass bg-panel2"
                    : "border-transparent hover:border-brass-dim hover:bg-panel2/60"
                )}
              >
                <span className="text-xl" aria-hidden>
                  {nation.flag}
                </span>
                <span className="sr-only">{nation.label}</span>
              </button>
            </li>
          );
        })}
      </ul>

      <AnimatePresence>
        {openNation && (
          <motion.div
            key={openNation}
            role="menu"
            initial={
              reduceMotion ? { opacity: 0 } : { x: -32, opacity: 0 }
            }
            animate={{ x: 0, opacity: 1 }}
            exit={reduceMotion ? { opacity: 0 } : { x: -32, opacity: 0 }}
            transition={
              reduceMotion
                ? { duration: 0.12 }
                : { type: "spring", stiffness: 340, damping: 26, mass: 0.7 }
            }
            className="absolute left-16 top-0 w-64 border-r border-hairline bg-panel/98 shadow-dossier backdrop-blur-sm sm:left-[72px]"
          >
            <div className="border-b border-hairline px-4 py-3">
              <p className="font-mono text-[10px] uppercase tracking-widest2 text-brass/80">
                Clearance filed under
              </p>
              <p className="font-display text-xl tracking-wide text-parchment">
                {NATIONS.find((n) => n.id === openNation)?.label}
              </p>
            </div>
            <ul className="p-2">
              {CATEGORIES.map((cat) => {
                const isActive =
                  activeSelection?.nation === openNation &&
                  activeSelection?.category === cat.id;
                return (
                  <li key={cat.id}>
                    <button
                      type="button"
                      role="menuitem"
                      onClick={() => {
                        onSelect(openNation, cat.id);
                        close();
                      }}
                      className={clsx(
                        "flex w-full items-center gap-3 rounded-sm px-3 py-2.5 text-left font-body text-sm transition-colors",
                        isActive
                          ? "bg-brass/15 text-brass"
                          : "text-parchment/80 hover:bg-panel2 hover:text-brass"
                      )}
                    >
                      <span aria-hidden className="text-base">
                        {cat.icon}
                      </span>
                      {cat.label}
                    </button>
                  </li>
                );
              })}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
