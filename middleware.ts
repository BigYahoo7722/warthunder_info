import createMiddleware from "next-intl/middleware";
import { routing } from "./i18n/routing";

export default createMiddleware(routing);

export const config = {
  // Run on everything except API routes, Next internals, and files with an
  // extension (favicon.ico, etc). /api/vehicles and /api/translate are
  // deliberately outside [locale] — they're backend endpoints, not
  // localized pages, so they shouldn't get a /fa or /ar prefix.
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
