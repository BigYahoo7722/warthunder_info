import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "War Thunder Codex — Field Dossier",
  description:
    "A complete, virtualized reference for the War Thunder vehicle roster.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/*
          Loaded via <link> rather than next/font/google on purpose:
          next/font/google needs to fetch the font file at BUILD time to
          generate its self-hosted output, so it hard-fails with no
          build-time network access. A <link> tag only feeds Next's
          optional font-optimization pass, which degrades gracefully
          instead (confirmed: `npm run build` in a network-restricted
          sandbox prints "Skipped optimizing this font" and finishes
          successfully rather than failing). Switch to next/font/google
          once you know your deploy target has open network access at
          build time — it's the better default there.
        */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Staatliches&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-ink font-body text-parchment antialiased">
        {children}
      </body>
    </html>
  );
}
