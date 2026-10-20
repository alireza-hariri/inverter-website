import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { getBrands, getSeoSettings } from "@/lib/content-api";
import { buildMeta } from "@/lib/seo";
import { categoryLabel, isLang, path, t, type Lang } from "@/lib/i18n";
import Breadcrumbs from "@/components/breadcrumbs";
import { BrandCard } from "@/components/cards";

export const dynamic = "force-dynamic";

const CATS = ["elevator", "industrial", "solar"] as const;

export async function generateMetadata({ params, searchParams }: { params: Promise<{ lang: string }>; searchParams: Promise<{ category?: string }> }): Promise<Metadata> {
  const { lang } = await params;
  if (!isLang(lang)) return {};
  const { category } = await searchParams;
  const settings = await getSeoSettings(lang).catch(() => null);
  const cat = CATS.includes(category as (typeof CATS)[number]) ? category! : "";
  // Category filters are views of one page: they share its canonical rather than compete with it.
  return buildMeta(lang, settings, {
    title: cat ? `${lang === "fa" ? "برندهای اینورتر" : "Inverter brands"} ${categoryLabel(cat, lang)}` : (lang === "fa" ? "برندهای تحت پوشش" : "Supported brands"),
    pathParts: ["brands"],
    page: cat ? undefined : settings?.pages.brands,
  });
}

export default async function BrandsPage({ params, searchParams }: { params: Promise<{ lang: string }>; searchParams: Promise<{ category?: string }> }) {
  const { lang } = await params;
  const sp = await searchParams;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const cat = CATS.includes(sp.category as (typeof CATS)[number]) ? sp.category! : undefined;
  const [page, settings] = await Promise.all([getBrands(l, cat), getSeoSettings(l).catch(() => null)]);
  const intro = settings?.pages.brands?.intro;
  const groups: Record<string, typeof page.results> = { elevator: [], industrial: [], solar: [] };
  for (const b of page.results) groups[b.category]?.push(b);
  return (
    <main className="container-x py-10">
      <Breadcrumbs items={[{ label: t("home", l), href: path(l) }, { label: t("brands", l) }]} />
      <h1 className="mt-4 text-3xl font-black">{t("supportedBrands", l)}{cat ? ` — ${categoryLabel(cat, l)}` : ""}</h1>
      {intro ? <p className="mt-2 max-w-3xl leading-8 text-slate-500">{intro}</p> : null}
      <div className="mt-4 flex flex-wrap gap-2">
        <Link href={path(l, "brands")} className={cat ? "btn-ghost text-sm" : "btn-gold text-sm !py-2"}>{l === "fa" ? "همه" : "All"}</Link>
        {CATS.map((c) => (
          <Link key={c} href={path(l, "brands") + `?category=${c}`} className={cat === c ? "btn-gold text-sm !py-2" : "btn-ghost text-sm"}>{categoryLabel(c, l)}</Link>
        ))}
      </div>
      {cat ? (
        <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">{page.results.map((b) => (<BrandCard key={b.slug} lang={l} b={b} />))}</div>
      ) : (
        (CATS.map((c) => (groups[c]?.length ? (
          <section key={c} className="mt-8">
            <h2 className="text-xl font-extrabold">{categoryLabel(c, l)}</h2>
            <div className="mt-3 grid grid-cols-2 gap-4 md:grid-cols-4">{groups[c].map((b) => (<BrandCard key={b.slug} lang={l} b={b} />))}</div>
          </section>
        ) : null)))
      )}
    </main>
  );
}
