import { apiRequest, asArray, asObject, asPage, withFields, type Check } from "./api";
import type {
  ArticleDetail,
  ArticleItem,
  BrandDetail,
  BrandItem,
  HomeContent,
  ServiceDetail,
  ServiceItem,
  SitemapRecord,
} from "@/types/content";
import type { Lang } from "./i18n";

function str(v: unknown): string {
  return typeof v === "string" ? v : "";
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
    seo: (r.seo as ServiceItem["seo"]) ?? { title: "", description: "", canonical_url: "", og_image: "", no_index: false, schema_type: "" },
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
    seo: (r.seo as BrandItem["seo"]) ?? { title: "", description: "", canonical_url: "", og_image: "", no_index: false, schema_type: "" },
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
    seo: (r.seo as ArticleItem["seo"]) ?? { title: "", description: "", canonical_url: "", og_image: "", no_index: false, schema_type: "" },
    published: Boolean(r.published),
    published_at: (r.published_at as string | null) ?? null,
    updated_at: str(r.updated_at),
  };
};

const asHome: Check<HomeContent> = (v, e) => {
  const r = asObject(v, e);
  withFields(r, e, ["site", "services", "brands", "articles"]);
  const site = asObject(r.site, e);
  return {
    language: str(r.language),
    site: {
      site_title: str(site.site_title),
      tagline: str(site.tagline),
      meta_description: str(site.meta_description),
      og_image: str(site.og_image),
      phone: str(site.phone),
      address: str(site.address),
      org_name: str(site.org_name),
    },
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

export function getHome(lang: Lang) {
  return apiRequest("/content/home/", asHome, { query: { language: lang } });
}

export function getServices(lang: Lang, page = 1) {
  return apiRequest("/services/", asPage(asServiceItem), {
    query: { language: lang, page, page_size: 20 },
  });
}

export function getService(lang: Lang, slug: string) {
  return apiRequest(`/services/${slug}/`, (v, e) => {
    const base = asServiceItem(v, e);
    const r = asObject(v, e);
    return {
      ...base,
      body: str(r.body),
      related_brands: asArray((r.related_brands ?? []) as unknown, e).map((x) => asObject(x, e) as unknown as ServiceDetail["related_brands"][number]),
      related_articles: asArray((r.related_articles ?? []) as unknown, e).map((x) => asObject(x, e) as unknown as ServiceDetail["related_articles"][number]),
    } as ServiceDetail;
  }, { query: { language: lang } });
}

export function getBrands(lang: Lang, category?: string, page = 1) {
  return apiRequest("/brands/", asPage(asBrandItem), {
    query: { language: lang, category: category ?? undefined, page, page_size: 30 },
  });
}

export function getBrand(lang: Lang, slug: string) {
  return apiRequest(`/brands/${slug}/`, (v, e) => {
    const base = asBrandItem(v, e);
    const r = asObject(v, e);
    return {
      ...base,
      content: str(r.content),
      related_services: asArray((r.related_services ?? []) as unknown, e).map((x) => asObject(x, e) as unknown as BrandDetail["related_services"][number]),
      related_articles: asArray((r.related_articles ?? []) as unknown, e).map((x) => asObject(x, e) as unknown as BrandDetail["related_articles"][number]),
    } as BrandDetail;
  }, { query: { language: lang } });
}

export function getArticles(lang: Lang, q?: string, page = 1) {
  return apiRequest("/articles/", asPage(asArticleItem), {
    query: { language: lang, search: q ?? undefined, page, page_size: 9 },
  });
}

export function getArticle(lang: Lang, slug: string) {
  return apiRequest(`/articles/${slug}/`, (v, e) => {
    const base = asArticleItem(v, e);
    const r = asObject(v, e);
    return {
      ...base,
      body: str(r.body),
      related_services: asArray((r.related_services ?? []) as unknown, e).map((x) => asObject(x, e) as unknown as ArticleDetail["related_services"][number]),
      related_brands: asArray((r.related_brands ?? []) as unknown, e).map((x) => asObject(x, e) as unknown as ArticleDetail["related_brands"][number]),
      related_articles: asArray((r.related_articles ?? []) as unknown, e).map((x) => asObject(x, e) as unknown as ArticleDetail["related_articles"][number]),
    } as ArticleDetail;
  }, { query: { language: lang } });
}

export function getSitemap(lang: Lang) {
  return apiRequest("/seo/sitemap/", asSitemap, { query: { language: lang } });
}
