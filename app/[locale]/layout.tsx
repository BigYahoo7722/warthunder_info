import type { Metadata } from "next";
import { NextIntlClientProvider } from "next-intl";
import { getMessages, getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import { routing, isRtl, type AppLocale } from "@/i18n/routing";
import { googleFontsHref, fontCssVars } from "@/lib/fonts";
import "../globals.css";

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export async function generateMetadata({
  params,
}: {
  params: { locale: string };
}): Promise<Metadata> {
  const { locale } = params;
  const t = await getTranslations({ locale, namespace: "meta" });
  return { title: t("title"), description: t("description") };
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  const { locale } = params;

  if (!routing.locales.includes(locale as AppLocale)) {
    notFound();
  }

  // Next 14 App Router: params are plain (synchronous) objects, not a
  // Promise — that change landed in Next 15. This project pins Next 14, so
  // don't `await params` here even though some next-intl example code
  // (written against Next 15) does.
  setRequestLocale(locale);

  const messages = await getMessages();
  const dir = isRtl(locale) ? "rtl" : "ltr";

  return (
    <html lang={locale} dir={dir}>
      <head>
        {/*
          Loaded via <link> rather than next/font/google on purpose:
          next/font/google needs to fetch the font file at BUILD time to
          generate its self-hosted output, so it hard-fails with no
          build-time network access. A <link> tag only feeds Next's
          optional font-optimization pass, which degrades gracefully
          instead. See README for the confirmed build output either way.
        */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href={googleFontsHref(locale as AppLocale)} rel="stylesheet" />
      </head>
      <body
        className="bg-ink font-body text-parchment antialiased"
        style={fontCssVars(locale as AppLocale)}
      >
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
