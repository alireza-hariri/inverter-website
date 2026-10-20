import { reportNotFound } from "@/lib/content-api";

/**
 * Receives the 404 page's beacon and forwards it to the admin's 404 monitor,
 * adding the ingest secret the browser must never see. The path is checked
 * against this site first -- only a URL that really answers 404 is logged --
 * so a stray or hostile POST cannot fill the monitor with junk.
 */
export async function POST(request: Request) {
  const body = (await request.json().catch(() => ({}))) as { path?: unknown; referrer?: unknown };
  const path = typeof body.path === "string" ? body.path : "";
  if (!/^\/(fa|en)(\/|$)/.test(path) || path.length > 300 || path.includes("//")) {
    return new Response(null, { status: 400 });
  }
  const check = await fetch(new URL(path, request.url), { method: "HEAD", redirect: "manual", cache: "no-store" }).catch(() => null);
  if (check?.status !== 404) return new Response(null, { status: 204 });
  const referrer = typeof body.referrer === "string" ? body.referrer.slice(0, 500) : "";
  await reportNotFound(path, referrer).catch(() => undefined);
  return new Response(null, { status: 204 });
}
