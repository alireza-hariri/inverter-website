/**
 * Everything the site tells search engines, built from what the SEO admin
 * edits (Django admin → SEO). Pages call `buildMeta` for their <head> and the
 * `*Ld` helpers for structured data; nothing else should hand-roll titles,
 * canonicals or schema.org objects, so a rule changed here changes everywhere.
 *
 * Precedence for every field is the same as Yoast's: the record's own SEO
 * field, then the fixed page's "Pages SEO" row, then the site default.
 */
import type { Metadata } from "next";
import type { Lang } from "./i18n";
import type { Faq, PageSeo, SeoBlock, SeoSettings } from "@/types/content";

export const SITE_URL = (process.env.NEXT_PUBLIC_SITE_URL ?? "https://electrogold.example.com").replace(/\/+$/, "");

export function siteUrl(lang: Lang, ...parts: string[]): string {
  return `${SITE_URL}/${lang}${parts.length ? "/" + parts.join("/") : ""}`;
}

/** Make a path or URL absolute against the public site. */
export function absUrl(pathOrUrl: string): string {
  if (!pathOrUrl) return "";
  return /^https?:\/\//.test(pathOrUrl) ? pathOrUrl : `${SITE_URL}${pathOrUrl.startsWith("/") ? "" : "/"}${pathOrUrl}`;
}

const DEFAULT_NAME = { fa: "الکتروگلد", en: "ElectroGold" } as const;

export function siteName(lang: Lang, settings: SeoSettings | null): string {
  return settings?.site.site_title || DEFAULT_NAME[lang];
}

type MetaOptions = {
  /** The page's own heading; becomes "Title | Site" unless an SEO title is set. */
  title: string;
  description?: string;
  pathParts?: string[];
  /** A record's SEO block (service, brand, article). */
  seo?: SeoBlock;
  /** A fixed page's row from "Pages SEO". */
  page?: PageSeo;
  image?: string;
  imageAlt?: string;
  type?: "website" | "article";
  publishedTime?: string | null;
  modifiedTime?: string;
  /** Force noindex, e.g. for search results or thin pages. */
  noIndex?: boolean;
  /** Appended to the canonical, e.g. "?page=2", so paginated pages are not folded into page 1. */
  canonicalQuery?: string;
};

export function buildMeta(lang: Lang, settings: SeoSettings | null, opts: MetaOptions): Metadata {
  const parts = opts.pathParts ?? [];
  const url = siteUrl(lang, ...parts) + (opts.canonicalQuery ?? "");
  const name = siteName(lang, settings);
  const sep = settings?.global.title_separator || "|";
  const explicit = opts.seo?.title || opts.page?.title;
  const title = explicit || (opts.title && opts.title !== name ? `${opts.title} ${sep} ${name}` : name);
  const description = opts.seo?.description || opts.page?.description || opts.description || settings?.site.meta_description || "";
  const image = opts.seo?.og_image || opts.image || opts.page?.og_image || settings?.global.default_og_image || settings?.site.og_image || "";
  const noIndex = Boolean(opts.noIndex || opts.seo?.no_index || opts.page?.no_index || settings?.global.discourage_search_engines);
  const images = image ? [{ url: absUrl(image), alt: opts.imageAlt || opts.seo?.image_alt || title }] : undefined;

  return {
    title: { absolute: title },
    description,
    alternates: {
      canonical: opts.seo?.canonical_url || url,
      languages: {
        fa: siteUrl("fa", ...parts),
        en: siteUrl("en", ...parts),
        "x-default": siteUrl("fa", ...parts),
      },
    },
    openGraph: {
      title,
      description,
      url,
      siteName: name,
      type: opts.type ?? "website",
      locale: lang === "fa" ? "fa_IR" : "en_US",
      alternateLocale: lang === "fa" ? ["en_US"] : ["fa_IR"],
      ...(images ? { images } : {}),
      ...(opts.type === "article"
        ? { publishedTime: opts.publishedTime ?? undefined, modifiedTime: opts.modifiedTime || undefined }
        : {}),
    },
    twitter: { card: images ? "summary_large_image" : "summary", title, description, ...(images ? { images: images.map((i) => i.url) } : {}) },
    robots: noIndex
      ? { index: false, follow: true }
      : { index: true, follow: true, googleBot: { index: true, follow: true, "max-image-preview": "large", "max-snippet": -1 } },
  };
}

// -- structured data ------------------------------------------------------

const ORG_ID = `${SITE_URL}/#organization`;
const SITE_ID = `${SITE_URL}/#website`;

/** The business, as LocalBusiness (or the subtype chosen in SEO settings). On every page. */
export function organizationLd(lang: Lang, settings: SeoSettings | null) {
  const g = settings?.global;
  const s = settings?.site;
  const type = g?.business_type || "ProfessionalService";
  const local = type !== "Organization";
  return {
    "@context": "https://schema.org",
    "@type": type,
    "@id": ORG_ID,
    name: g?.org_schema_name || s?.org_name || siteName(lang, settings),
    alternateName: s?.site_title || undefined,
    url: g?.org_schema_url || siteUrl(lang),
    logo: g?.org_logo ? absUrl(g.org_logo) : undefined,
    image: g?.org_logo || g?.default_og_image ? absUrl(g.org_logo || g.default_og_image) : undefined,
    description: s?.meta_description || undefined,
    telephone: s?.phone || undefined,
    email: s?.email || undefined,
    sameAs: g?.same_as?.length ? g.same_as : undefined,
    ...(local
      ? {
          address: s?.address
            ? { "@type": "PostalAddress", streetAddress: s.address, addressLocality: s.city || undefined, addressCountry: "IR" }
            : undefined,
          geo: g?.latitude && g?.longitude ? { "@type": "GeoCoordinates", latitude: g.latitude, longitude: g.longitude } : undefined,
          openingHours: g?.opening_hours ? g.opening_hours.split(",").map((x) => x.trim()).filter(Boolean) : undefined,
          priceRange: g?.price_range || undefined,
          areaServed: { "@type": "Country", name: lang === "fa" ? "ایران" : "Iran" },
        }
      : {}),
  };
}

export function websiteLd(lang: Lang, settings: SeoSettings | null) {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "@id": SITE_ID,
    url: siteUrl(lang),
    name: siteName(lang, settings),
    inLanguage: lang === "fa" ? "fa-IR" : "en-US",
    publisher: { "@id": ORG_ID },
    potentialAction: {
      "@type": "SearchAction",
      target: { "@type": "EntryPoint", urlTemplate: `${siteUrl(lang, "articles")}?q={search_term_string}` },
      "query-input": "required name=search_term_string",
    },
  };
}

export function breadcrumbLd(items: { label: string; href?: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((it, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: it.label,
      ...(it.href ? { item: absUrl(it.href) } : {}),
    })),
  };
}

export function faqLd(faqs: Faq[]) {
  if (!faqs.length) return null;
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqs.map((f) => ({
      "@type": "Question",
      name: f.question,
      acceptedAnswer: { "@type": "Answer", text: f.answer },
    })),
  };
}

export function serviceLd(lang: Lang, s: { title: string; summary: string; slug: string; image: string; category: string; seo: SeoBlock }, brands: string[]) {
  return {
    "@context": "https://schema.org",
    "@type": s.seo.schema_type || "Service",
    name: s.title,
    serviceType: s.title,
    description: s.seo.description || s.summary,
    url: siteUrl(lang, "services", s.slug),
    image: s.image ? absUrl(s.image) : undefined,
    provider: { "@id": ORG_ID },
    areaServed: { "@type": "Country", name: lang === "fa" ? "ایران" : "Iran" },
    ...(brands.length ? { brand: brands.map((name) => ({ "@type": "Brand", name })) } : {}),
  };
}

export function articleLd(lang: Lang, settings: SeoSettings | null, a: {
  title: string; excerpt: string; slug: string; image: string; author: string;
  published_at: string | null; updated_at: string; seo: SeoBlock; body: string;
}) {
  const url = siteUrl(lang, "articles", a.slug);
  return {
    "@context": "https://schema.org",
    "@type": a.seo.schema_type && a.seo.schema_type !== "Service" ? a.seo.schema_type : "BlogPosting",
    headline: (a.seo.title || a.title).slice(0, 110),
    description: a.seo.description || a.excerpt,
    image: a.image ? [absUrl(a.image)] : undefined,
    datePublished: a.published_at || undefined,
    dateModified: a.updated_at || a.published_at || undefined,
    author: a.author ? { "@type": "Organization", name: a.author, url: siteUrl(lang, "about") } : { "@id": ORG_ID },
    publisher: { "@id": ORG_ID },
    mainEntityOfPage: { "@type": "WebPage", "@id": url },
    url,
    inLanguage: lang === "fa" ? "fa-IR" : "en-US",
    wordCount: a.body ? a.body.replace(/<[^>]+>/g, " ").split(/\s+/).filter(Boolean).length : undefined,
  };
}
