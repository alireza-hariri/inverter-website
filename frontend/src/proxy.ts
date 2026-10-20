/**
 * Runs before every page request (Next 16's replacement for middleware).
 *
 * - Applies the redirects managed in the admin (SEO → Redirects), so the SEO
 *   specialist can fix a moved URL without a deploy. The list is fetched from
 *   the backend and kept for REDIRECT_TTL_MS; a backend outage keeps serving
 *   the last good list rather than dropping every redirect.
 * - Sends `/` to the Persian home with a permanent redirect.
 * - Passes the page language to the app as a request header: the root layout
 *   needs it for `<html lang dir>`.
 */
import { NextResponse, type NextRequest } from "next/server";
import { getRedirects } from "@/lib/content-api";
import type { RedirectRule } from "@/types/content";

const REDIRECT_TTL_MS = 60_000;
let rules: Map<string, RedirectRule> = new Map();
let fetchedAt = 0;
let inflight: Promise<void> | null = null;

function normalise(path: string): string {
  let p = path;
  try {
    p = decodeURI(path);
  } catch {
    /* keep the raw path */
  }
  return p.replace(/\/+$/, "") || "/";
}

async function loadRules(): Promise<Map<string, RedirectRule>> {
  if (Date.now() - fetchedAt > REDIRECT_TTL_MS && !inflight) {
    inflight = getRedirects()
      .then((list) => {
        rules = new Map(list.map((r) => [normalise(r.old_path), r]));
      })
      .catch(() => {
        /* backend down: keep the last list */
      })
      .finally(() => {
        fetchedAt = Date.now();
        inflight = null;
      });
  }
  if (inflight && fetchedAt === 0) await inflight;
  return rules;
}

export async function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;

  if (pathname === "/") {
    return NextResponse.redirect(new URL(`/fa${search}`, request.url), 308);
  }

  const rule = (await loadRules()).get(normalise(pathname));
  if (rule) {
    if (rule.status_code === 410) {
      return new NextResponse("Gone", { status: 410, headers: { "X-Robots-Tag": "noindex" } });
    }
    const target = new URL(rule.new_path, request.url);
    if (!target.search) target.search = search;
    return NextResponse.redirect(target, rule.status_code);
  }

  const headers = new Headers(request.headers);
  const lang = pathname.match(/^\/(fa|en)(\/|$)/)?.[1] ?? "fa";
  headers.set("x-site-lang", lang);
  return NextResponse.next({ request: { headers } });
}

export const config = {
  // Everything but Next internals and static assets -- old URLs ending in
  // .html or .php (a WordPress migration) must still reach the redirect table.
  matcher: ["/((?!api/|_next/static|_next/image|.*\\.(?:png|jpe?g|gif|svg|webp|avif|ico|woff2?|ttf|css|js|map|txt|xml)$).*)"],
};
