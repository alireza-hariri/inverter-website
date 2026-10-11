import type { MetadataRoute } from "next";
import { getSitemap } from "@/lib/content-api";
const SITE_URL = (process.env.NEXT_PUBLIC_SITE_URL ?? "https://electrogold.example.com").replace(/\/+$/, "");
function urlFor(route: string, slug: string, lang: string): string | null {
  const base = `/`;
  switch (route) {
    case "home": return base;
    case "services": return `/services`;
    case "service": return `/services/`;
    case "brands": return `/brands`;
    case "brand": return `/brands/`;
    case "articles": return `/articles`;
    case "article": return `/articles/`;
    case "about": return `/about`;
    case "contact": return `/contact`;
    default: return null;
  }
}
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const out: MetadataRoute.Sitemap = [];
  for (const lang of ["fa", "en"] as const) {
    try {
      const records = await getSitemap(lang);
      for (const r of records) {
        if (r.no_index) continue;
        const url = urlFor(r.route, r.slug, lang);
        if (!url) continue;
        out.push({ url, lastModified: r.updated_at || undefined, alternates: { languages: { fa: urlFor(r.route, r.slug, "fa")!, en: urlFor(r.route, r.slug, "en")! } } });
      }
    } catch { /* backend unreachable at build: fall back to static routes */ }
  }
  if (!out.length) {
    for (const lang of ["fa", "en"]) for (const p of ["", "/services", "/brands", "/articles", "/about", "/contact"]) out.push({ url: `/` });
  }
  return out;
}
