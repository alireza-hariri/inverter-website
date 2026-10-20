import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { nullIfNotFound } from "@/lib/api";
import { getArticle, getSeoSettings } from "@/lib/content-api";
import { articleLd, buildMeta } from "@/lib/seo";
import { fmtDate, isLang, path, readingTime, t, type Lang } from "@/lib/i18n";
import Breadcrumbs from "@/components/breadcrumbs";
import { RelatedArticles } from "@/components/cards";
import DetailSidebar from "@/components/detail-sidebar";
import FaqList from "@/components/faq-list";
import { RichBody } from "@/components/rich-body";
import { JsonLd } from "@/components/states";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ lang: string; slug: string }> }): Promise<Metadata> {
  const { lang, slug } = await params;
  if (!isLang(lang)) return {};
  const [a, settings] = await Promise.all([getArticle(lang, slug).catch(nullIfNotFound), getSeoSettings(lang).catch(() => null)]);
  if (!a) return {};
  return buildMeta(lang, settings, {
    title: a.title, description: a.excerpt, pathParts: ["articles", slug], seo: a.seo, image: a.image,
    type: "article", publishedTime: a.published_at, modifiedTime: a.updated_at,
  });
}

export default async function ArticleDetailPage({ params }: { params: Promise<{ lang: string; slug: string }> }) {
  const { lang, slug } = await params;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const fa = l === "fa";
  const [a, settings] = await Promise.all([getArticle(l, slug).catch(nullIfNotFound), getSeoSettings(l).catch(() => null)]);
  if (!a) notFound();
  const crumbs = [{ label: t("home", l), href: path(l) }, { label: t("articles", l), href: path(l, "articles") }, { label: a.title }];
  const meta = [
    a.author,
    a.published_at ? <time key="d" dateTime={a.published_at}>{fmtDate(a.published_at, l)}</time> : null,
    a.reading_minutes ? readingTime(a.reading_minutes, l) : null,
  ].filter(Boolean);
  return (
    <main>
      <JsonLd data={articleLd(l, settings, a)} />
      <header className="page-hero">
        <div className="container-x max-w-4xl py-10 md:py-14">
          <Breadcrumbs items={crumbs} />
          <h1 className="mt-5 text-3xl font-black leading-[1.5] md:text-4xl">{a.title}</h1>
          <p className="mt-3 flex flex-wrap gap-x-3 text-sm text-slate-500">
            {meta.map((m, i) => <span key={i}>{i ? <span aria-hidden="true" className="me-3">·</span> : null}{m}</span>)}
          </p>
        </div>
      </header>
      <div className="container-x grid gap-10 py-10 lg:grid-cols-[minmax(0,1fr)_300px]">
        <div className="min-w-0 max-w-3xl">
          {a.image ? <img src={a.image} alt={a.seo.image_alt || a.title} className="mb-8 aspect-[16/9] w-full rounded-2xl object-cover" width={1200} height={675} /> : null}
          {a.excerpt ? <p className="lead">{a.excerpt}</p> : null}
          <article className="mt-6"><RichBody html={a.body_html} /></article>
          <FaqList faqs={a.faqs} title={fa ? "سوالات متداول" : "FAQ"} />
          {(a.related_services.length > 0 || a.related_brands.length > 0) ? (
            <div className="mt-10 flex flex-wrap gap-2">
              {a.related_services.map((s) => <Link key={s.slug} href={path(l, "services", s.slug)} className="chip">{s.title}</Link>)}
              {a.related_brands.map((b) => <Link key={b.slug} href={path(l, "brands", b.slug)} className="chip">{b.name}</Link>)}
            </div>
          ) : null}
          <RelatedArticles lang={l} articles={a.related_articles} />
        </div>
        <DetailSidebar lang={l} toc={a.toc} phone={settings?.site.phone} />
      </div>
    </main>
  );
}
