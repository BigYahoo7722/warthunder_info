import { NextRequest, NextResponse } from "next/server";

/**
 * Wraps DeepL's translate endpoint. This needs a real DeepL API key in
 * DEEPL_API_KEY — sign up at https://www.deepl.com/pro-api (there's a free
 * tier, 500k chars/month, good enough for development) and set it as an
 * environment variable locally (.env.local) and in your Vercel project
 * settings. I can't provision this for you; there's no working key in this
 * codebase, and the route below returns a clear 501 rather than pretending
 * to work if the key is missing.
 *
 * To use Google Cloud Translation instead: swap ENDPOINT/buildRequest/
 * parseResponse below. The contract this route exposes to the frontend
 * (POST {texts, targetLocale} -> {translations}) doesn't need to change.
 */

const DEEPL_ENDPOINT = "https://api-free.deepl.com/v2/translate"; // use api.deepl.com (no "-free") on a paid plan

// DeepL's language codes mostly match this app's locale codes, but not all
// — this maps the ones that differ. Anything not listed is passed through
// uppercased, which is what DeepL expects.
const DEEPL_TARGET_LANG: Record<string, string> = {
  zh: "ZH",
  pt: "PT-PT", // DeepL splits PT-PT/PT-BR; change if you need Brazilian Portuguese
  en: "EN-US",
};

const MAX_TEXTS_PER_REQUEST = 50;

interface TranslateRequestBody {
  texts: string[];
  targetLocale: string;
}

export async function POST(req: NextRequest) {
  const apiKey = process.env.DEEPL_API_KEY;
  if (!apiKey) {
    return NextResponse.json(
      {
        error: "missing_api_key",
        message: "DEEPL_API_KEY is not set on the server. See this route's file header for setup steps.",
      },
      { status: 501 }
    );
  }

  let body: TranslateRequestBody;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "invalid_body" }, { status: 400 });
  }

  const { texts, targetLocale } = body;
  if (!Array.isArray(texts) || texts.length === 0 || typeof targetLocale !== "string") {
    return NextResponse.json({ error: "invalid_body" }, { status: 400 });
  }
  if (texts.length > MAX_TEXTS_PER_REQUEST) {
    return NextResponse.json(
      { error: "too_many_texts", message: `Max ${MAX_TEXTS_PER_REQUEST} texts per request — chunk on the client.` },
      { status: 400 }
    );
  }

  const targetLang = DEEPL_TARGET_LANG[targetLocale] ?? targetLocale.toUpperCase();

  try {
    const upstream = await fetch(DEEPL_ENDPOINT, {
      method: "POST",
      headers: {
        Authorization: `DeepL-Auth-Key ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: texts, target_lang: targetLang }),
    });

    if (!upstream.ok) {
      const detail = await upstream.text().catch(() => "");
      return NextResponse.json(
        { error: "upstream_error", status: upstream.status, detail },
        { status: 502 }
      );
    }

    const data: { translations: Array<{ text: string }> } = await upstream.json();
    return NextResponse.json({
      translations: data.translations.map((t) => t.text),
    });
  } catch (err) {
    return NextResponse.json(
      { error: "network_error", message: err instanceof Error ? err.message : String(err) },
      { status: 502 }
    );
  }
}
