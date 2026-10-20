import type { MetadataRoute } from "next";
import { getSitemap } from "@/lib/content-api";
import { LANGS, type Lang } from "@/lib/i18n";
import { siteUrl } from "@/lib/seo";

export const dynamic = "force-dynamic";

const STATIC_ROUTES: Record<string, string[]> = {
  home: [], services: ["services"], brands: ["brands"], articles: ["articles"], about: ["about"], contact: ["contact"],
};
const DETAIL_ROUTES: Record<string, string> = { service: "services", brand: "brands", article: "articles" };
const PRIORITY: Record<string, number> = { home: 1, services: 0.9, service: 0.9, brands: 0.7, brand: 0.7, articles: 0.7, article: 0.6 };

function partsFor(route: string, slug: string): string[] | null {
  if (route in STATIC_ROUTES) return STATIC_ROUTES[route];
  if (route in DETAIL_ROUTES && slug) return [DETAIL_ROUTES[route], slug];
  return null;
}

/**
 * Every indexable page in both languages, each with its hreflang alternates.
 * The backend decides what is indexable (published, not noindex, not
 * scheduled); this only turns its records into absolute URLs.
 */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const out: MetadataRoute.Sitemap = [];
  for (const lang of LANGS) {
    // No fallback: a sitemap missing every record would read as "those pages
    // are gone". Failing keeps search engines on the last good copy.
    const records = await getSitemap(lang);
    for (const r of records) {
      if (r.no_index) continue;
      const parts = partsFor(r.route, r.slug);
      if (!parts) continue;
      const alt = (l: Lang) => siteUrl(l, ...parts);
      out.push({
        url: alt(lang),
        lastModified: r.updated_at || undefined,
        changeFrequency: r.route === "home" || r.route === "articles" ? "weekly" : "monthly",
        priority: PRIORITY[r.route] ?? 0.5,
        alternates: { languages: { fa: alt("fa"), en: alt("en"), "x-default": alt("fa") } },
      });
    }
  }
  return out;
}
