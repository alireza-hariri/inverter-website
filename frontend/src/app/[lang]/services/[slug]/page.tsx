import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getService } from "@/lib/content-api";
import { metaFor, siteUrl } from "@/lib/seo";
import { categoryLabel, isLang, path, t, type Lang } from "@/lib/i18n";
import Breadcrumbs from "@/components/breadcrumbs";
import { JsonLd } from "@/components/states";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ lang: string; slug: string }> }): Promise<Metadata> {
  const { lang, slug } = await params;
  if (!isLang(lang)) return {};
  try {
    const s = await getService(lang, slug);
    return metaFor(lang, { title: s.seo.title || s.title, description: s.seo.description || s.summary, pathParts: ["services", slug], seo: s.seo });
  } catch {
    return {};
  }
}

export default async function ServiceDetailPage({ params }: { params: Promise<{ lang: string; slug: string }> }) {
  const { lang, slug } = await params;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const s = await getService(l, slug).catch(() => null);
  if (!s) notFound();
  return (
    <main className="container-x py-10">
      <Breadcrumbs items={[{ label: t("home", l), href: path(l) }, { label: t("services", l), href: path(l, "services") }, { label: s.title }]} />
      <JsonLd data={{ "@context": "https://schema.org", "@type": "Service", name: s.title, description: s.summary, url: siteUrl(l, "services", s.slug) }} />
      <span className="chip mt-4 inline-block">{categoryLabel(s.category, l)}</span>
      <h1 className="mt-2 text-3xl font-black">{s.title}</h1>
      <p className="mt-3 text-slate-600 leading-8">{s.summary}</p>
      <article className="card prose-body mt-6 p-6 whitespace-pre-line leading-8">{s.body || s.summary}</article>
      {s.related_brands.length > 0 ? (
        <section className="mt-8">
          <h2 className="text-xl font-extrabold">{t("supportedBrands", l)}</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {s.related_brands.map((b) => (
              <Link key={b.slug} href={path(l, "brands", b.slug)} className="btn-ghost text-sm" dir="ltr">{b.name || b.slug}</Link>
            ))}
          </div>
        </section>
      ) : null}
      {s.related_articles.length > 0 ? (
        <section className="mt-8">
          <h2 className="text-xl font-extrabold">{t("relatedArticles", l)}</h2>
          <ul className="mt-3 space-y-2">
            {s.related_articles.map((a) => (
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
