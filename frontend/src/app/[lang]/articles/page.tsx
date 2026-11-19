import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { nullIfNotFound } from "@/lib/api";
import { getArticles, getSeoSettings } from "@/lib/content-api";
import { buildMeta } from "@/lib/seo";
import { isLang, num, path, t, type Lang } from "@/lib/i18n";
import Breadcrumbs from "@/components/breadcrumbs";
import { ArticleCard } from "@/components/cards";
import { EmptyState } from "@/components/states";
import type { ArticleType } from "@/types/content";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params, searchParams }: { params: Promise<{ lang: string }>; searchParams: Promise<{ q?: string | string[]; page?: string | string[]; article_type?: string | string[] }> }): Promise<Metadata> {
  const { lang } = await params;
  if (!isLang(lang)) return {};
  const sp = await searchParams;
  const pageNum = Math.max(1, Number(typeof sp.page === "string" ? sp.page : 1) || 1);
  const articleType = sp.article_type === "general" || sp.article_type === "brand_specific" ? sp.article_type : undefined;
  const settings = await getSeoSettings(lang).catch(() => null);
  const base = lang === "fa" ? "مقالات آموزشی" : "Articles";
  const typeTitle = articleType
    ? lang === "fa" ? articleType === "general" ? "مقالات عمومی" : "مقالات اختصاصی برندها"
      : articleType === "general" ? "General articles" : "Brand-specific guides"
    : base;
  return buildMeta(lang, settings, {
    title: pageNum > 1 ? `${typeTitle} — ${lang === "fa" ? "صفحه" : "page"} ${num(pageNum, lang)}` : typeTitle,
    pathParts: ["articles"],
    // Page 1's SEO title would make every page a duplicate of it.
    page: pageNum > 1 || articleType ? undefined : settings?.pages.articles,
    canonicalQuery: pageNum > 1 ? `?page=${pageNum}` : "",
    // Internal search results are thin, endless pages: keep them out of the index.
    noIndex: Boolean(sp.q || articleType),
  });
}

export default async function ArticlesPage({ params, searchParams }: { params: Promise<{ lang: string }>; searchParams: Promise<{ q?: string | string[]; page?: string | string[]; article_type?: string | string[] }> }) {
  const { lang } = await params;
  const sp = await searchParams;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const q = typeof sp.q === "string" ? sp.q : "";
  const pageNum = Math.max(1, Number(typeof sp.page === "string" ? sp.page : 1) || 1);
  const articleType: ArticleType | undefined = sp.article_type === "general" || sp.article_type === "brand_specific"
    ? sp.article_type : undefined;
  const [data, settings] = await Promise.all([getArticles(l, q || undefined, pageNum, articleType).catch(nullIfNotFound), getSeoSettings(l).catch(() => null)]);
  // The backend answers 404 for a page number past the last one.
  if (!data) notFound();
  const intro = settings?.pages.articles?.intro;
  const totalPages = Math.max(1, Math.ceil(data.count / 9));
  const fa = l === "fa";
  const filterHref = (type?: ArticleType) => {
    const query = new URLSearchParams();
    if (q) query.set("q", q);
    if (type) query.set("article_type", type);
    const suffix = query.toString();
    return path(l, "articles") + (suffix ? `?${suffix}` : "");
  };
  const filters: { type?: ArticleType; label: string }[] = [
    { label: fa ? "همهٔ مقاله‌ها" : "All articles" },
    { type: "general", label: fa ? "مقالات عمومی" : "General" },
    { type: "brand_specific", label: fa ? "مقالات اختصاصی برندها" : "Brand-specific" },
  ];
  return (
    <main className="container-x py-10">
      <Breadcrumbs items={[{ label: t("home", l), href: path(l) }, { label: t("articles", l) }]} />
      <h1 className="mt-4 text-3xl font-black">{t("articles", l)}</h1>
      {intro ? <p className="mt-2 max-w-3xl leading-8 text-slate-500">{intro}</p> : null}
      <nav aria-label={fa ? "دسته‌بندی مقالات" : "Article categories"} className="mt-5 flex flex-wrap gap-2">
        {filters.map((filter) => {
          const active = (filter.type ?? "") === (articleType ?? "");
          return <Link key={filter.type ?? "all"} href={filterHref(filter.type)} aria-current={active ? "page" : undefined}
            className={active ? "btn-gold !py-2 !px-4 text-sm" : "btn-ghost !py-2 !px-4 text-sm"}>{filter.label}</Link>;
        })}
      </nav>
      <form method="get" role="search" className="mt-5 flex max-w-xl gap-2">
        <input name="q" type="search" defaultValue={q} placeholder={t("searchPlaceholder", l)} aria-label={t("search", l)} className="field" />
        {articleType ? <input type="hidden" name="article_type" value={articleType} /> : null}
        <button className="btn-gold shrink-0" type="submit">{t("search", l)}</button>
      </form>
      <div className="mt-6">
        {data.results.length === 0 ? (
          <EmptyState lang={l} query={q} />
        ) : (
          <>
            <div className="grid gap-5 md:grid-cols-3">{data.results.map((a) => (<ArticleCard key={a.slug} lang={l} a={a} />))}</div>
            {totalPages > 1 ? (
              <nav className="mt-8 flex items-center justify-center gap-2" aria-label="pagination">
                {Array.from({ length: totalPages }).map((_, i) => {
                  const p = i + 1;
                  const href = path(l, "articles") + `?${new URLSearchParams({ ...(q ? { q } : {}), ...(articleType ? { article_type: articleType } : {}), page: String(p) }).toString()}`;
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
