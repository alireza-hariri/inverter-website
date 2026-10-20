import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { nullIfNotFound } from "@/lib/api";
import { getSeoSettings, getService } from "@/lib/content-api";
import { buildMeta, serviceLd } from "@/lib/seo";
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
  const [s, settings] = await Promise.all([getService(lang, slug).catch(nullIfNotFound), getSeoSettings(lang).catch(() => null)]);
  if (!s) return {};
  return buildMeta(lang, settings, { title: s.title, description: s.summary, pathParts: ["services", slug], seo: s.seo, image: s.image });
}

export default async function ServiceDetailPage({ params }: { params: Promise<{ lang: string; slug: string }> }) {
  const { lang, slug } = await params;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const fa = l === "fa";
  const [s, settings] = await Promise.all([getService(l, slug).catch(nullIfNotFound), getSeoSettings(l).catch(() => null)]);
  if (!s) notFound();
  const crumbs = [{ label: t("home", l), href: path(l) }, { label: t("services", l), href: path(l, "services") }, { label: s.title }];
  return (
    <main>
      <JsonLd data={serviceLd(l, s, s.related_brands.map((b) => b.name || b.slug))} />
      <header className="page-hero">
        <div className="container-x py-10 md:py-14">
          <Breadcrumbs items={crumbs} />
          <span className="chip mt-5 inline-block">{categoryLabel(s.category, l)}</span>
          <h1 className="mt-3 max-w-3xl text-3xl font-black leading-tight md:text-4xl">{s.title}</h1>
          <p className="mt-4 max-w-3xl text-lg leading-9 text-slate-600">{s.summary}</p>
        </div>
      </header>
      <div className="container-x grid gap-10 py-10 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="min-w-0">
          {s.image ? <img src={s.image} alt={s.seo.image_alt || s.title} className="mb-8 aspect-[16/8] w-full rounded-2xl object-cover" width={1200} height={600} /> : null}
          <article><RichBody html={s.body_html} fallback={s.summary} /></article>
          <FaqList faqs={s.faqs} title={fa ? `سوالات متداول ${s.title}` : `${s.title}: FAQ`} />
          <RelatedArticles lang={l} articles={s.related_articles} />
        </div>
        <DetailSidebar lang={l} toc={s.toc} phone={settings?.site.phone}>
          {s.related_brands.length > 0 ? (
            <div className="card p-5">
              <div className="font-extrabold">{t("supportedBrands", l)}</div>
              <div className="mt-3 flex flex-wrap gap-2">
                {s.related_brands.map((b) => (
                  <Link key={b.slug} href={path(l, "brands", b.slug)} className="chip hover:bg-[#ffefb8]">{b.name || b.slug}</Link>
                ))}
              </div>
            </div>
          ) : null}
        </DetailSidebar>
      </div>
    </main>
  );
}
