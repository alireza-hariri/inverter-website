import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getArticle } from "@/lib/content-api";
import { metaFor, siteUrl } from "@/lib/seo";
import { fmtDate, isLang, path, t, type Lang } from "@/lib/i18n";
import Breadcrumbs from "@/components/breadcrumbs";
import { JsonLd } from "@/components/states";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ lang: string; slug: string }> }): Promise<Metadata> {
  const { lang, slug } = await params;
  if (!isLang(lang)) return {};
  try {
    const a = await getArticle(lang, slug);
    return metaFor(lang, { title: a.seo.title || a.title, description: a.seo.description || a.excerpt, pathParts: ["articles", slug], seo: a.seo, type: "article" });
  } catch {
    return {};
  }
}

export default async function ArticleDetailPage({ params }: { params: Promise<{ lang: string; slug: string }> }) {
  const { lang, slug } = await params;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const a = await getArticle(l, slug).catch(() => null);
  if (!a) notFound();
  return (
    <main className="container-x py-10 max-w-4xl">
      <Breadcrumbs items={[{ label: t("home", l), href: path(l) }, { label: t("articles", l), href: path(l, "articles") }, { label: a.title }]} />
      <JsonLd data={{ "@context": "https://schema.org", "@type": "Article", headline: a.title, description: a.excerpt, author: a.author, datePublished: a.published_at, url: siteUrl(l, "articles", a.slug) }} />
      <h1 className="mt-4 text-3xl font-black leading-12">{a.title}</h1>
      <p className="mt-2 text-sm text-slate-400">{[a.author, fmtDate(a.published_at, l)].filter(Boolean).join(" • ")}</p>
      <p className="card mt-4 p-4 text-slate-600 leading-8" style={{ background: "#fffbe8" }}>{a.excerpt}</p>
      <article className="card prose-body mt-4 p-6 whitespace-pre-line">{a.body}</article>
      {a.related_articles.length > 0 ? (
        <section className="mt-8">
          <h2 className="text-xl font-extrabold">{t("relatedArticles", l)}</h2>
          <ul className="mt-3 space-y-2">
            {a.related_articles.map((r) => (
              <li key={r.slug}><Link className="text-[#8a6a00] font-bold hover:underline" href={path(l, "articles", r.slug)}>{r.title || r.slug}</Link></li>
            ))}
          </ul>
        </section>
      ) : null}
      <div className="card mt-8 p-6 text-center" style={{ background: "#fffbe8" }}>
        <p className="font-extrabold">{t("contactCta", l)}</p>
        <Link href={path(l, "contact")} className="btn-gold mt-3 inline-block">{t("requestService", l)}</Link>
      </div>
    </main>
  );
}
