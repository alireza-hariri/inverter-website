import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getArticles } from "@/lib/content-api";
import { metaFor } from "@/lib/seo";
import { isLang, num, path, t, type Lang } from "@/lib/i18n";
import Breadcrumbs from "@/components/breadcrumbs";
import { ArticleCard } from "@/components/cards";
import { EmptyState } from "@/components/states";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ lang: string }> }): Promise<Metadata> {
  const { lang } = await params;
  if (!isLang(lang)) return {};
  return metaFor(lang, { title: lang === "fa" ? "مقالات آموزشی | الکتروگلد" : "Blog articles | ElectroGold", pathParts: ["articles"] });
}

export default async function ArticlesPage({ params, searchParams }: { params: Promise<{ lang: string }>; searchParams: Promise<{ q?: string; page?: string }> }) {
  const { lang } = await params;
  const sp = await searchParams;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const q = sp.q ?? "";
  const pageNum = Math.max(1, Number(sp.page ?? 1) || 1);
  const data = await getArticles(l, q || undefined, pageNum).catch(() => null);
  const totalPages = data ? Math.max(1, Math.ceil(data.count / 9)) : 1;
  const fa = l === "fa";
  return (
    <main className="container-x py-10">
      <Breadcrumbs items={[{ label: t("home", l), href: path(l) }, { label: t("articles", l) }]} />
      <h1 className="mt-4 text-3xl font-black">{t("articles", l)}</h1>
      <form method="get" className="mt-5 flex gap-2">
        <input name="q" defaultValue={q} placeholder={t("searchPlaceholder", l)} className="field" />
        <button className="btn-gold shrink-0" type="submit">{t("search", l)}</button>
      </form>
      <div className="mt-6">
        {!data || data.results.length === 0 ? (
          <EmptyState lang={l} query={q} />
        ) : (
          <>
            <div className="grid gap-4 md:grid-cols-3">{data.results.map((a) => (<ArticleCard key={a.slug} lang={l} a={a} />))}</div>
            {totalPages > 1 ? (
              <nav className="mt-8 flex items-center justify-center gap-2" aria-label="pagination">
                {Array.from({ length: totalPages }).map((_, i) => {
                  const p = i + 1;
                  const href = path(l, "articles") + `?${new URLSearchParams({ ...(q ? { q } : {}), page: String(p) }).toString()}`;
                  return <Link key={p} href={href} className={p === pageNum ? "btn-gold !py-2 !px-4 text-sm" : "btn-ghost !py-2 !px-4 text-sm"}>{num(p, l)}</Link>;
                })}
              </nav>
            ) : null}
            <p className="mt-4 text-center text-xs text-slate-400">{fa ? `مجموع: ${num(data.count, l)} مقاله` : `Total: ${data.count} articles`}</p>
          </>
        )}
      </div>
    </main>
  );
}
