import { NextRequest, NextResponse } from "next/server";
import { revalidateTag } from "next/cache";

/**
 * Webhook the GitHub Action calls right after a successful scrape, so
 * fresh data shows up in seconds rather than waiting out the hourly
 * unstable_cache window in app/api/vehicles/route.ts. This is optional
 * infrastructure — the site self-heals within REVALIDATE_SECONDS even if
 * this is never called, which is why the workflow step that hits it is
 * best-effort (see .github/workflows/daily-scraper.yml).
 *
 * Protected by a shared secret rather than left open — anyone who can
 * trigger this can force extra MongoDB reads on the next request to each
 * tag. Set REVALIDATE_SECRET in Vercel's env vars and pass the same value
 * as the REVALIDATE_SECRET GitHub Actions secret.
 */
export async function POST(req: NextRequest) {
  const expected = process.env.REVALIDATE_SECRET;
  if (!expected) {
    return NextResponse.json(
      { error: "REVALIDATE_SECRET not configured on the server" },
      { status: 501 }
    );
  }

  let body: { secret?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "invalid_body" }, { status: 400 });
  }

  if (body.secret !== expected) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  revalidateTag("vehicles");
  return NextResponse.json({ revalidated: true, tag: "vehicles", at: new Date().toISOString() });
}
