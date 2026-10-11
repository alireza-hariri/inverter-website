import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getBrand } from "@/lib/content-api";
import { metaFor, siteUrl } from "@/lib/seo";
import { categoryLabel, isLang, path, t, type Lang } from "@/lib/i18n";
import Breadcrumbs from "@/components/breadcrumbs";
import { JsonLd } from "@/components/states";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ lang: string; slug: string }> }): Promise<Metadata> {
  const { lang, slug } = await params;
  if (!isLang(lang)) return {};
  try {
    const b = await getBrand(lang, slug);
    return metaFor(lang, { title: b.seo.title || b.name, description: b.seo.description || b.description, pathParts: ["brands", slug], seo: b.seo });
  } catch {
    return {};
  }
}

export default async function BrandDetailPage({ params }: { params: Promise<{ lang: string; slug: string }> }) {
  const { lang, slug } = await params;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const b = await getBrand(l, slug).catch(() => null);
  if (!b) notFound();
  return (
    <main className="container-x py-10">
      <Breadcrumbs items={[{ label: t("home", l), href: path(l) }, { label: t("brands", l), href: path(l, "brands") }, { label: b.name }]} />
      <JsonLd data={{ "@context": "https://schema.org", "@type": "Brand", name: b.name, description: b.description, url: siteUrl(l, "brands", b.slug) }} />
      <span className="chip mt-4 inline-block">{categoryLabel(b.category, l)}</span>
      <h1 className="mt-2 text-3xl font-black" dir="ltr">{b.name}</h1>
      <p className="mt-3 text-slate-600 leading-8">{b.description}</p>
      <article className="card prose-body mt-6 p-6 whitespace-pre-line">{b.content || b.description}</article>
      {b.related_services.length > 0 ? (
        <section className="mt-8">
          <h2 className="text-xl font-extrabold">{t("relatedServices", l)}</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {b.related_services.map((s) => (
              <Link key={s.slug} href={path(l, "services", s.slug)} className="btn-ghost text-sm">{s.title || s.slug}</Link>
            ))}
          </div>
        </section>
      ) : null}
      {b.related_articles.length > 0 ? (
        <section className="mt-8">
          <h2 className="text-xl font-extrabold">{t("relatedArticles", l)}</h2>
          <ul className="mt-3 space-y-2">
            {b.related_articles.map((a) => (
              <li key={a.slug}><Link className="text-[#8a6a00] font-bold hover:underline" href={path(l, "articles", a.slug)}>{a.title || a.slug}</Link></li>
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
