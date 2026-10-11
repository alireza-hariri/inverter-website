import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { getBrands } from "@/lib/content-api";
import { metaFor } from "@/lib/seo";
import { categoryLabel, isLang, path, t, type Lang } from "@/lib/i18n";
import Breadcrumbs from "@/components/breadcrumbs";
import { BrandCard } from "@/components/cards";

export const dynamic = "force-dynamic";

const CATS = ["elevator", "industrial", "solar"] as const;

export async function generateMetadata({ params }: { params: Promise<{ lang: string }> }): Promise<Metadata> {
  const { lang } = await params;
  if (!isLang(lang)) return {};
  return metaFor(lang, { title: lang === "fa" ? "برندهای تحت پوشش | الکتروگلد" : "Supported brands | ElectroGold", pathParts: ["brands"] });
}

export default async function BrandsPage({ params, searchParams }: { params: Promise<{ lang: string }>; searchParams: Promise<{ category?: string }> }) {
  const { lang } = await params;
  const sp = await searchParams;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const cat = CATS.includes(sp.category as (typeof CATS)[number]) ? sp.category! : undefined;
  const page = await getBrands(l, cat).catch(() => null);
  const groups: Record<string, typeof page extends null ? never : NonNullable<typeof page>["results"]> = { elevator: [], industrial: [], solar: [] };
  for (const b of page?.results ?? []) groups[b.category]?.push(b);
  return (
    <main className="container-x py-10">
      <Breadcrumbs items={[{ label: t("home", l), href: path(l) }, { label: t("brands", l) }]} />
      <h1 className="mt-4 text-3xl font-black">{t("brands", l)}</h1>
      <div className="mt-4 flex flex-wrap gap-2">
        <Link href={path(l, "brands")} className={cat ? "btn-ghost text-sm" : "btn-gold text-sm !py-2"}>{l === "fa" ? "همه" : "All"}</Link>
        {CATS.map((c) => (
          <Link key={c} href={path(l, "brands") + `?category=${c}`} className={cat === c ? "btn-gold text-sm !py-2" : "btn-ghost text-sm"}>{categoryLabel(c, l)}</Link>
        ))}
      </div>
      {cat ? (
        <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">{(page?.results ?? []).map((b) => (<BrandCard key={b.slug} lang={l} b={b} />))}</div>
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
