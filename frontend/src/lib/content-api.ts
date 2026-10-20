import { cache } from "react";
import { apiRequest, asArray, asObject, asPage, withFields, type Check } from "./api";
import type {
  ArticleDetail,
  ArticleItem,
  BrandDetail,
  BrandItem,
  Faq,
  GlobalSeo,
  HomeContent,
  HomeSite,
  PageSeo,
  RedirectRule,
  RelatedLink,
  SeoBlock,
  SeoSettings,
  ServiceDetail,
  ServiceItem,
  SitemapRecord,
  TocEntry,
} from "@/types/content";
import type { Lang } from "./i18n";

function str(v: unknown): string {
  return typeof v === "string" ? v : "";
}

function asSeo(v: unknown): SeoBlock {
  const r = v && typeof v === "object" ? (v as Record<string, unknown>) : {};
  return {
    title: str(r.title),
    description: str(r.description),
    canonical_url: str(r.canonical_url),
    og_image: str(r.og_image),
    no_index: Boolean(r.no_index),
    schema_type: str(r.schema_type),
    image_alt: str(r.image_alt),
  };
}

function asFaqs(v: unknown, e: string): Faq[] {
  return asArray(v ?? [], e).map((x) => {
    const r = asObject(x, e);
    return { question: str(r.question), answer: str(r.answer) };
  });
}

function asToc(v: unknown, e: string): TocEntry[] {
  return asArray(v ?? [], e).map((x) => {
    const r = asObject(x, e);
    return { id: str(r.id), text: str(r.text), level: Number(r.level ?? 2) };
  });
}

/** The short links a detail page lists for its related records. */
function asLinks(v: unknown, e: string): RelatedLink[] {
  return asArray(v ?? [], e).map((x) => {
    const r = asObject(x, e);
    withFields(r, e, ["slug"]);
    return {
      slug: str(r.slug),
      title: str(r.title) || undefined,
      name: str(r.name) || undefined,
      category: str(r.category) || undefined,
      image: str(r.image) || undefined,
    };
  });
}

const SITE_KEYS = ["site_title", "tagline", "hero_title", "hero_subtitle", "meta_description", "og_image", "phone",
  "whatsapp", "email", "address", "city", "org_name", "opening_hours_text"] as const;

function asSite(v: unknown, e: string): HomeSite {
  const r = asObject(v, e);
  return Object.fromEntries(SITE_KEYS.map((k) => [k, str(r[k])])) as HomeSite;
}

const asServiceItem: Check<ServiceItem> = (v, e) => {
  const r = asObject(v, e);
  withFields(r, e, ["slug", "category", "title"]);
  return {
    slug: str(r.slug),
    category: str(r.category),
    title: str(r.title),
    summary: str(r.summary),
    image: str(r.image),
    seo: asSeo(r.seo),
    published: Boolean(r.published),
    ordering: Number(r.ordering ?? 0),
    updated_at: str(r.updated_at),
  };
};

const asBrandItem: Check<BrandItem> = (v, e) => {
  const r = asObject(v, e);
  withFields(r, e, ["slug", "category", "name"]);
  return {
    slug: str(r.slug),
    category: str(r.category),
    name: str(r.name),
    description: str(r.description),
    logo: str(r.logo),
    seo: asSeo(r.seo),
    published: Boolean(r.published),
    ordering: Number(r.ordering ?? 0),
    updated_at: str(r.updated_at),
  };
};

const asArticleItem: Check<ArticleItem> = (v, e) => {
  const r = asObject(v, e);
  withFields(r, e, ["slug", "title"]);
  return {
    slug: str(r.slug),
    title: str(r.title),
    excerpt: str(r.excerpt),
    image: str(r.image),
    author: str(r.author),
    seo: asSeo(r.seo),
    published: Boolean(r.published),
    published_at: (r.published_at as string | null) ?? null,
    updated_at: str(r.updated_at),
    reading_minutes: Number(r.reading_minutes ?? 0),
  };
};

const asHome: Check<HomeContent> = (v, e) => {
  const r = asObject(v, e);
  withFields(r, e, ["site", "services", "brands", "articles"]);
  return {
    language: str(r.language),
    site: asSite(r.site, e),
    faqs: asFaqs(r.faqs, e),
    services: asArray(r.services, e).map((x) => asServiceItem(x, e)),
    brands: asArray(r.brands, e).map((x) => asBrandItem(x, e)),
    articles: asArray(r.articles, e).map((x) => asArticleItem(x, e)),
  };
};

const asSitemap: Check<SitemapRecord[]> = (v, e) => {
  const r = asObject(v, e);
  return asArray(r.results, e).map((x) => {
    const rec = asObject(x, e);
    return {
      route: str(rec.route),
      slug: str(rec.slug),
      updated_at: str(rec.updated_at),
      no_index: Boolean(rec.no_index),
    };
  });
};

/** Cached per request: the layout, the page and its metadata all read it. */
export const getHome = cache((lang: Lang) =>
  apiRequest("/content/home/", asHome, { query: { language: lang } }));

export function getServices(lang: Lang, page = 1) {
  return apiRequest("/services/", asPage(asServiceItem), {
    query: { language: lang, page, page_size: 20 },
  });
}

export const getService = cache((lang: Lang, slug: string) => {
  return apiRequest(`/services/${slug}/`, (v, e) => {
    const base = asServiceItem(v, e);
    const r = asObject(v, e);
    return {
      ...base,
      body: str(r.body),
      body_html: str(r.body_html),
      toc: asToc(r.toc, e),
      faqs: asFaqs(r.faqs, e),
      related_brands: asLinks(r.related_brands, e),
      related_articles: asLinks(r.related_articles, e),
    } as ServiceDetail;
  }, { query: { language: lang } });
});

export function getBrands(lang: Lang, category?: string, page = 1) {
  return apiRequest("/brands/", asPage(asBrandItem), {
    query: { language: lang, category: category ?? undefined, page, page_size: 30 },
  });
}

export const getBrand = cache((lang: Lang, slug: string) => {
  return apiRequest(`/brands/${slug}/`, (v, e) => {
    const base = asBrandItem(v, e);
    const r = asObject(v, e);
    return {
      ...base,
      content: str(r.content),
      content_html: str(r.content_html),
      toc: asToc(r.toc, e),
      faqs: asFaqs(r.faqs, e),
      related_services: asLinks(r.related_services, e),
      related_articles: asLinks(r.related_articles, e),
    } as BrandDetail;
  }, { query: { language: lang } });
});

export function getArticles(lang: Lang, q?: string, page = 1) {
  return apiRequest("/articles/", asPage(asArticleItem), {
    query: { language: lang, search: q ?? undefined, page, page_size: 9 },
  });
}

export const getArticle = cache((lang: Lang, slug: string) => {
  return apiRequest(`/articles/${slug}/`, (v, e) => {
    const base = asArticleItem(v, e);
    const r = asObject(v, e);
    return {
      ...base,
      body: str(r.body),
      body_html: str(r.body_html),
      toc: asToc(r.toc, e),
      faqs: asFaqs(r.faqs, e),
      related_services: asLinks(r.related_services, e),
      related_brands: asLinks(r.related_brands, e),
      related_articles: asLinks(r.related_articles, e),
    } as ArticleDetail;
  }, { query: { language: lang } });
});

export function getSitemap(lang: Lang) {
  return apiRequest("/seo/sitemap/", asSitemap, { query: { language: lang } });
}

const asSeoSettings: Check<SeoSettings> = (v, e) => {
  const r = asObject(v, e);
  withFields(r, e, ["site", "global", "pages"]);
  const g = asObject(r.global, e);
  const ver = (g.verification && typeof g.verification === "object" ? g.verification : {}) as Record<string, unknown>;
  const pages: Record<string, PageSeo> = {};
  for (const [key, raw] of Object.entries(asObject(r.pages, e))) {
    const p = asObject(raw, e);
    pages[key] = { page: key, title: str(p.title), description: str(p.description), intro: str(p.intro),
      og_image: str(p.og_image), no_index: Boolean(p.no_index) };
  }
  const global: GlobalSeo = {
    canonical_host: str(g.canonical_host), title_separator: str(g.title_separator) || "|",
    discourage_search_engines: Boolean(g.discourage_search_engines), default_og_image: str(g.default_og_image),
    org_schema_name: str(g.org_schema_name), org_schema_url: str(g.org_schema_url), org_logo: str(g.org_logo),
    business_type: str(g.business_type) || "ProfessionalService", opening_hours: str(g.opening_hours),
    price_range: str(g.price_range), latitude: str(g.latitude), longitude: str(g.longitude),
    same_as: Array.isArray(g.same_as) ? g.same_as.map(String) : [],
    verification: { google: str(ver.google), bing: str(ver.bing), yandex: str(ver.yandex) },
    gtm_id: str(g.gtm_id), ga4_id: str(g.ga4_id),
  };
  return { site: asSite(r.site, e), global, pages };
};

/** Site identity, global SEO settings and per-page SEO. Cached per request. */
export const getSeoSettings = cache((lang: Lang) =>
  apiRequest("/seo/settings/", asSeoSettings, { query: { language: lang } }));

export function getRedirects() {
  return apiRequest("/seo/redirects/", (v, e) => asArray(asObject(v, e).results, e).map((x) => {
    const r = asObject(x, e);
    return { old_path: str(r.old_path), new_path: str(r.new_path), status_code: Number(r.status_code) } as RedirectRule;
  }));
}

export function getRobots() {
  return apiRequest("/seo/robots/", (v, e) => str(asObject(v, e).content));
}

/** Tells the admin's 404 monitor about a broken URL. Server-side only: it carries the ingest secret. */
export function reportNotFound(path: string, referrer: string) {
  return apiRequest("/seo/not-found/", () => undefined, {
    method: "POST",
    body: { path, referrer },
    headers: process.env.SEO_INGEST_TOKEN ? { "X-Seo-Token": process.env.SEO_INGEST_TOKEN } : {},
  });
}
