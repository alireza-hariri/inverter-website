import type { Metadata } from "next";
import type { Lang } from "./i18n";
import type { SeoBlock } from "@/types/content";

const SITE_URL = (process.env.NEXT_PUBLIC_SITE_URL ?? "https://electrogold.example.com").replace(/\/+$/, "");

export function siteUrl(lang: Lang, ...parts: string[]): string {
  return `${SITE_URL}/${lang}${parts.length ? "/" + parts.join("/") : ""}`;
}

export function canonicalFor(lang: Lang, seo: SeoBlock | undefined, fallback: string): string {
  if (seo?.canonical_url) return seo.canonical_url;
  return fallback;
}

export function metaFor(
  lang: Lang,
  opts: {
    title: string;
    description?: string;
    pathParts?: string[];
    seo?: SeoBlock;
    image?: string;
    type?: "website" | "article";
  },
): Metadata {
  const url = siteUrl(lang, ...(opts.pathParts ?? []));
  const title = opts.seo?.title || opts.title;
  const description = opts.seo?.description || opts.description || "";
  const other: Lang = lang === "fa" ? "en" : "fa";
  const otherUrl = siteUrl(other, ...(opts.pathParts ?? []));
  return {
    title,
    description,
    alternates: {
      canonical: canonicalFor(lang, opts.seo, url),
      languages: { fa: siteUrl("fa", ...(opts.pathParts ?? [])), en: otherUrl },
    },
    openGraph: {
      title,
      description,
      url,
      type: opts.type ?? "website",
      locale: lang === "fa" ? "fa_IR" : "en_US",
      ...(opts.image || opts.seo?.og_image ? { images: [{ url: opts.image || opts.seo!.og_image }] } : {}),
    },
    robots: opts.seo?.no_index ? { index: false, follow: false } : undefined,
  };
}
