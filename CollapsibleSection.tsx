"use client";

import { useState, type ReactNode } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import clsx from "clsx";

export function CollapsibleSection({
  title,
  eyebrow,
  defaultOpen = false,
  children,
}: {
  title: string;
  eyebrow?: string;
  defaultOpen?: boolean;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const reduceMotion = useReducedMotion();

  return (
    <div className="border-b border-hairline last:border-b-0">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className={clsx(
          "tab-cut flex w-full items-center justify-between gap-3 border-l-2 bg-panel2/60 px-4 py-2.5 text-left transition-colors",
          open ? "border-brass" : "border-hairline hover:border-brass-dim"
        )}
      >
        <span className="flex items-baseline gap-2">
          {eyebrow && (
            <span className="font-mono text-[10px] uppercase tracking-widest2 text-parchment/40">
              {eyebrow}
            </span>
          )}
          <span className="font-display text-base tracking-wide text-parchment">
            {title}
          </span>
        </span>
        <span
          className={clsx(
            "font-mono text-xs text-brass transition-transform",
            open && "rotate-180"
          )}
          aria-hidden
        >
          ▾
        </span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={reduceMotion ? undefined : { height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={reduceMotion ? undefined : { height: 0, opacity: 0 }}
            transition={{ duration: 0.22, ease: "easeOut" }}
            className="overflow-hidden"
          >
            <div className="px-4 py-3">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
