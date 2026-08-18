import type { Config } from "tailwindcss";

// Design tokens — see README.md "Design language" section for the reasoning
// behind each choice. Do not add ad-hoc hex values in components; extend
// this palette instead so the dossier aesthetic stays consistent.
const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#0B0C08",      // base background — warm near-black, not neutral/blue-black
        panel: "#15170F",    // card & drawer surface
        panel2: "#1B1D14",   // raised surface (modal, active row)
        hairline: "#33362A", // borders/dividers — muted olive-grey
        parchment: "#E8E4D6",// primary text — aged-paper tinted white
        brass: "#C7A046",    // signature accent — stamps, active tab, key numerals
        "brass-dim": "#8F7434",
        redact: "#8B2A22",   // rare/event tag only — muted oxblood, used sparingly
      },
      fontFamily: {
        display: ["var(--font-display)", "Staatliches", "sans-serif"],
        body: ["var(--font-body)", '"IBM Plex Sans"', "sans-serif"],
        mono: ["var(--font-mono)", '"IBM Plex Mono"', "monospace"],
      },
      letterSpacing: {
        widest2: "0.28em",
      },
      boxShadow: {
        dossier: "0 20px 60px -20px rgba(0,0,0,0.6)",
      },
    },
  },
  plugins: [],
};

export default config;
