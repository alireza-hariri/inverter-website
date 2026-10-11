import Link from "next/link";
import type { Metadata } from "next";
import { getHome } from "@/lib/content-api";
import { metaFor } from "@/lib/seo";
import { isLang, path, t, type Lang } from "@/lib/i18n";
import Hero from "@/components/hero";
import { ArticleCard, BrandCard, ServiceCard, SectionHeading } from "@/components/cards";
import { JsonLd } from "@/components/states";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ lang: string }> }): Promise<Metadata> {
  const { lang } = await params;
  if (!isLang(lang)) return {};
  try {
    const home = await getHome(lang);
    return metaFor(lang, { title: home.site.site_title, description: home.site.meta_description || home.site.tagline, pathParts: [] });
  } catch {
    return {};
  }
}

export default async function HomePage({ params }: { params: Promise<{ lang: string }> }) {
  const { lang } = await params;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const fa = l === "fa";
  let home;
  try {
    home = await getHome(l);
  } catch {
    return (
      <main className="container-x py-16">
        <div className="card p-10 text-center">
          <p className="font-bold">{t("errorText", l)}</p>
          <Link className="btn-gold mt-5 inline-block" href={path(l, "contact")}>{t("contact", l)}</Link>
        </div>
      </main>
    );
  }
  return (
    <main>
      <Hero lang={l} title={home.site.site_title} tagline={home.site.tagline} />
      <JsonLd data={{ "@context": "https://schema.org", "@type": "Organization", name: home.site.org_name || home.site.site_title, telephone: home.site.phone, address: home.site.address }} />
      <div className="container-x py-12 space-y-14">
        <section>
          <SectionHeading title={t("ourServices", l)} link={{ href: path(l, "services"), label: t("services", l) }} />
          <div className="grid gap-4 md:grid-cols-3">
            {home.services.map((s) => (<ServiceCard key={s.slug} lang={l} s={s} />))}
          </div>
        </section>
        <section className="hero-bg rounded-2xl p-8 text-white">
          <h2 className="text-2xl font-extrabold">{t("process", l)}</h2>
          <div className="mt-5 grid gap-3 md:grid-cols-4 text-sm">
            {(fa ? ["۱. ثبت درخواست و مشاوره", "۲. عیب‌یابی تخصصی", "۳. تعمیر و تست زیر بار", "۴. تحویل با گارانتی"] : ["1. Request & consultation", "2. Expert diagnostics", "3. Repair & load testing", "4. Delivery with warranty"]).map((x) => (
              <div key={x} className="rounded-xl border border-white/15 bg-white/5 p-4 font-bold">{x}</div>
            ))}
          </div>
        </section>
        <section>
          <SectionHeading title={t("brands", l)} link={{ href: path(l, "brands"), label: t("brands", l) }} />
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {home.brands.map((b) => (<BrandCard key={b.slug} lang={l} b={b} />))}
          </div>
        </section>
        <section>
          <SectionHeading title={t("featuredArticles", l)} link={{ href: path(l, "articles"), label: t("articles", l) }} />
          <div className="grid gap-4 md:grid-cols-3">
            {home.articles.map((a) => (<ArticleCard key={a.slug} lang={l} a={a} />))}
          </div>
        </section>
        <section className="card p-8 text-center" style={{ borderColor: "#f3d97b", background: "#fffbe8" }}>
          <h2 className="text-xl font-extrabold">{t("contactCta", l)}</h2>
          <Link href={path(l, "contact")} className="btn-gold mt-4">{t("requestService", l)}</Link>
        </section>
      </div>
    </main>
  );
}
