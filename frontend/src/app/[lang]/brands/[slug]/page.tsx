import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { nullIfNotFound } from "@/lib/api";
import { getBrand, getSeoSettings } from "@/lib/content-api";
import { buildMeta, siteUrl } from "@/lib/seo";
import { categoryLabel, isLang, path, t, type Lang } from "@/lib/i18n";
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
  const [b, settings] = await Promise.all([getBrand(lang, slug).catch(nullIfNotFound), getSeoSettings(lang).catch(() => null)]);
  if (!b) return {};
  return buildMeta(lang, settings, {
    title: lang === "fa" ? `تعمیر اینورتر ${b.name}` : `${b.name} inverter repair`,
    description: b.description, pathParts: ["brands", slug], seo: b.seo,
  });
}

export default async function BrandDetailPage({ params }: { params: Promise<{ lang: string; slug: string }> }) {
  const { lang, slug } = await params;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const fa = l === "fa";
  const [b, settings] = await Promise.all([getBrand(l, slug).catch(nullIfNotFound), getSeoSettings(l).catch(() => null)]);
  if (!b) notFound();
  const crumbs = [{ label: t("home", l), href: path(l) }, { label: t("brands", l), href: path(l, "brands") }, { label: b.name }];
  return (
    <main>
      <JsonLd data={{ "@context": "https://schema.org", "@type": "Brand", name: b.name, description: b.description, url: siteUrl(l, "brands", b.slug) }} />
      <header className="page-hero">
        <div className="container-x py-10 md:py-14">
          <Breadcrumbs items={crumbs} />
          <span className="chip mt-5 inline-block">{categoryLabel(b.category, l)}</span>
          <h1 className="mt-3 text-3xl font-black md:text-4xl">{fa ? `تعمیر اینورتر ${b.name}` : `${b.name} inverter repair`}</h1>
          <p className="mt-4 max-w-3xl text-lg leading-9 text-slate-600">{b.description}</p>
        </div>
      </header>
      <div className="container-x grid gap-10 py-10 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="min-w-0">
          <article><RichBody html={b.content_html} fallback={b.description} /></article>
          <FaqList faqs={b.faqs} title={fa ? "سوالات متداول" : "FAQ"} />
          <RelatedArticles lang={l} articles={b.related_articles} />
        </div>
        <DetailSidebar lang={l} toc={b.toc} phone={settings?.site.phone}>
          {b.related_services.length > 0 ? (
            <div className="card p-5">
              <div className="font-extrabold">{t("relatedServices", l)}</div>
              <ul className="mt-3 space-y-2">
                {b.related_services.map((s) => (
                  <li key={s.slug}><Link href={path(l, "services", s.slug)} className="link-arrow text-sm">{s.title || s.slug}</Link></li>
                ))}
              </ul>
            </div>
          ) : null}
        </DetailSidebar>
      </div>
    </main>
  );
}
