"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslations } from "next-intl";
import clsx from "clsx";
import { NATIONS, CATEGORIES } from "@/lib/taxonomy";
import { useRtlFlip } from "@/lib/direction";
import type { Category, Nation } from "@/lib/types";

const TAB_HEIGHT_PX = 52;
const TAB_LIST_TOP_PADDING_PX = 12; // matches the ul's py-3 below

export function Sidebar({
  onSelect,
  activeSelection,
}: {
  onSelect: (nation: Nation, category: Category) => void;
  activeSelection: { nation: Nation; category: Category } | null;
}) {
  const t = useTranslations();
  const [openNation, setOpenNation] = useState<Nation | null>(null);
  const flip = useRtlFlip();
  const rootRef = useRef<HTMLElement>(null);

  const close = () => setOpenNation(null);

  // Click-to-open / click-outside-to-close. This replaces a previous
  // hover-based version that had a real bug: the drawer was pinned to the
  // top of the sidebar regardless of which tab opened it, so for a tab near
  // the bottom (Sweden, Israel, China...) the mouse had to travel a long
  // diagonal to reach it, crossing empty space outside any hoverable
  // element along the way — which fired mouseleave and closed the drawer
  // before the pointer arrived. Switching to click removes the failure
  // mode entirely instead of patching the gap; the drawer's position is
  // also now aligned to the clicked tab (see drawerTop below) rather than
  // teleporting to the top, since that would still look broken even
  // without the hover bug.
  useEffect(() => {
    if (!openNation) return;
    const handlePointerDown = (e: PointerEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        close();
      }
    };
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") close();
    };
    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [openNation]);

  const openIndex = openNation ? NATIONS.findIndex((n) => n.id === openNation) : -1;
  const drawerTop = TAB_LIST_TOP_PADDING_PX + Math.max(openIndex, 0) * TAB_HEIGHT_PX;

  return (
    <nav
      ref={rootRef}
      aria-label={t("sidebar.navLabel")}
      className="relative z-30 flex h-full shrink-0"
    >
      <ul className="flex w-16 flex-col border-e border-hairline bg-panel py-3 sm:w-[72px]">
        {NATIONS.map((nation) => {
          const isOpen = openNation === nation.id;
          const isActive = activeSelection?.nation === nation.id;
          return (
            <li key={nation.id}>
              <button
                type="button"
                onClick={() =>
                  setOpenNation((prev) => (prev === nation.id ? null : nation.id))
                }
                aria-haspopup="true"
                aria-expanded={isOpen}
                style={{ height: TAB_HEIGHT_PX }}
                className={clsx(
                  "tab-cut group relative flex w-full items-center justify-center border-s-2 transition-colors",
                  isOpen || isActive
                    ? "border-brass bg-panel2"
                    : "border-transparent hover:border-brass-dim hover:bg-panel2/60"
                )}
              >
                <span className="text-xl" aria-hidden>
                  {nation.flag}
                </span>
                <span className="sr-only">{t(`nation.${nation.id}`)}</span>
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
            initial={{ x: flip(-32), opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: flip(-32), opacity: 0 }}
            transition={{ type: "spring", stiffness: 340, damping: 26, mass: 0.7 }}
            style={{
              top: drawerTop,
              maxHeight: `calc(100% - ${drawerTop}px - 16px)`,
            }}
            className="absolute start-16 z-10 w-64 overflow-y-auto border-e border-hairline bg-panel/98 shadow-dossier backdrop-blur-sm sm:start-[72px]"
          >
            <div className="border-b border-hairline px-4 py-3">
              <p className="font-mono text-[10px] uppercase tracking-widest2 text-brass/80">
                {t("sidebar.clearanceFiledUnder")}
              </p>
              <p className="font-display text-xl tracking-wide text-parchment">
                {t(`nation.${openNation}`)}
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
                        "flex w-full items-center gap-3 rounded-sm px-3 py-2.5 text-start font-body text-sm transition-colors",
                        isActive
                          ? "bg-brass/15 text-brass"
                          : "text-parchment/80 hover:bg-panel2 hover:text-brass"
                      )}
                    >
                      <span aria-hidden className="text-base">
                        {cat.icon}
                      </span>
                      {t(`category.${cat.id}`)}
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
