import { createClient, type SupabaseClient } from "@supabase/supabase-js";

/**
 * Read-only client using the anon key + the public-read RLS policy from
 * scripts/supabase-schema.sql. Unlike lib/mongodb.ts in the previous
 * version of this app, there's no connection-pool-exhaustion risk to
 * guard against here — Supabase's JS client talks to PostgREST over
 * plain HTTPS, not a persistent connection pool, so each query is just an
 * independent request. This module-level singleton is for convenience
 * (skip re-reading env vars and re-constructing the client on every call)
 * rather than to avoid resource exhaustion the way the MongoDB version
 * needed.
 *
 * Deliberately NOT using NEXT_PUBLIC_ env var names, even though the anon
 * key is designed to be safe for browser exposure in other architectures
 * — in this app, every Supabase call happens server-side inside
 * app/api/vehicles/route.ts, so there's no reason to ship it to the
 * client bundle at all.
 */

let cachedClient: SupabaseClient | undefined;

export function hasSupabaseConfigured(): boolean {
  return Boolean(process.env.SUPABASE_URL && process.env.SUPABASE_ANON_KEY);
}

export function getSupabaseClient(): SupabaseClient {
  if (cachedClient) return cachedClient;

  const url = process.env.SUPABASE_URL;
  const anonKey = process.env.SUPABASE_ANON_KEY;
  if (!url || !anonKey) {
    throw new Error("SUPABASE_URL / SUPABASE_ANON_KEY are not set — see README 'Database setup'.");
  }

  cachedClient = createClient(url, anonKey, {
    auth: { persistSession: false }, // server-side only, no browser session to persist
  });
  return cachedClient;
}
