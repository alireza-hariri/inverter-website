import { getRobots } from "@/lib/content-api";
import { SITE_URL } from "@/lib/seo";

export const dynamic = "force-dynamic";

/**
 * robots.txt as written in the admin (SEO settings → robots.txt), with the
 * sitemap line added here so it always carries the real public origin. If the
 * backend is down, allow crawling rather than serve a 500, which Google treats
 * as "crawl nothing".
 */
export async function GET() {
  const body = (await getRobots().catch(() => "User-agent: *\nAllow: /"))
    .split("\n")
    .filter((line) => !/^\s*sitemap\s*:/i.test(line))
    .join("\n")
    .trim();
  return new Response(`${body}\n\nSitemap: ${SITE_URL}/sitemap.xml\n`, {
    headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "public, max-age=300" },
  });
}
