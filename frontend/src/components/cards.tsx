import Link from "next/link";
import type { Lang } from "@/lib/i18n";
import { categoryLabel, fmtDate, path, readingTime, t } from "@/lib/i18n";
import type { ArticleItem, BrandItem, RelatedLink, ServiceItem } from "@/types/content";
import SafeImg from "./safe-img";

const CATEGORY_ICON: Record<string, string> = { elevator: "⇅", industrial: "⚙", solar: "☀" };

/** Latin wordmarks for the brand wall; unknown slugs fall back to the slug itself. */
const BRAND_LATIN: Record<string, string> = { hpmont: "HPMont" };
const brandLatin = (slug: string) => BRAND_LATIN[slug] ?? slug.charAt(0).toUpperCase() + slug.slice(1);

export function SectionHeading({ title, sub, eyebrow, link, as = "h2" }: {
  title: string; sub?: string; eyebrow?: string; link?: { href: string; label: string }; as?: "h2" | "h1";
}) {
  const H = as;
  return (
    <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
      <div className="max-w-2xl">
        {eyebrow ? <div className="eyebrow">{eyebrow}</div> : null}
        <H className="text-2xl md:text-3xl font-black leading-tight">{title}</H>
        {sub ? <p className="mt-2 text-slate-500 leading-8">{sub}</p> : null}
      </div>
      {link ? <Link href={link.href} className="link-arrow shrink-0">{link.label}</Link> : null}
    </div>
  );
}

function Thumb({ src, alt, icon, ratio = "aspect-[16/10]" }: { src: string; alt: string; icon?: string; ratio?: string }) {
  return (
    <div className={`thumb ${ratio}`}>
      <span className="thumb__icon" aria-hidden="true">{icon ?? "⚡"}</span>
      <SafeImg src={src} alt={alt} loading="lazy" decoding="async" width={640} height={400} />
    </div>
  );
}

export function ServiceCard({ lang, s, className = "" }: { lang: Lang; s: ServiceItem; className?: string }) {
  return (
    <Link href={path(lang, "services", s.slug)} className={`card card-hover group flex flex-col ${className}`}>
      <Thumb src={s.image} alt={s.seo.image_alt || s.title} icon={CATEGORY_ICON[s.category]} />
      <div className="flex flex-1 flex-col p-5">
        <span className="chip self-start">{categoryLabel(s.category, lang)}</span>
        <h3 className="mt-3 text-lg font-extrabold group-hover:text-[#8a6a00]">{s.title}</h3>
        <p className="mt-2 flex-1 text-sm leading-7 text-slate-500 line-clamp-3">{s.summary}</p>
        <span className="link-arrow mt-4 text-sm">{t("readMore", lang)}</span>
      </div>
    </Link>
  );
}

export function BrandCard({ lang, b }: { lang: Lang; b: BrandItem }) {
  return (
    <Link href={path(lang, "brands", b.slug)} className="card card-hover group block p-5 text-center">
      <div className="brand-mark mx-auto" aria-hidden="true">{b.name.slice(0, 1)}</div>
      <h3 className="mt-3 font-extrabold group-hover:text-[#8a6a00]">{b.name}</h3>
      <div className="mt-1 text-xs text-slate-400">{categoryLabel(b.category, lang)}</div>
      <p className="mt-2 text-xs leading-6 text-slate-500 line-clamp-2">{b.description}</p>
    </Link>
  );
}

/** Compact wordmark tile for the homepage brand wall. */
export function BrandTile({ lang, b }: { lang: Lang; b: BrandItem }) {
  return (
    <Link href={path(lang, "brands", b.slug)} className="brand-tile group">
      <span className="brand-tile__latin" dir="ltr">{brandLatin(b.slug)}</span>
      <span className="brand-tile__meta">{lang === "fa" ? b.name + " · " : ""}{categoryLabel(b.category, lang)}</span>
    </Link>
  );
}

export function ArticleCard({ lang, a }: { lang: Lang; a: ArticleItem }) {
  const meta = [fmtDate(a.published_at, lang), a.reading_minutes ? readingTime(a.reading_minutes, lang) : ""].filter(Boolean).join(" · ");
  return (
    <Link href={path(lang, "articles", a.slug)} className="card card-hover group flex flex-col">
      <Thumb src={a.image} alt={a.seo.image_alt || a.title} icon="✎" ratio="aspect-[16/9]" />
      <div className="flex flex-1 flex-col p-5">
        {meta ? <div className="text-xs text-slate-400">{meta}</div> : null}
        <h3 className="mt-2 font-extrabold leading-7 line-clamp-2 group-hover:text-[#8a6a00]">{a.title}</h3>
        <p className="mt-2 flex-1 text-sm leading-7 text-slate-500 line-clamp-2">{a.excerpt}</p>
        <span className="link-arrow mt-3 text-sm">{t("readMore", lang)}</span>
      </div>
    </Link>
  );
}

/** The "Related articles" list under a detail page's body. Renders nothing when empty. */
export function RelatedArticles({ lang, articles }: { lang: Lang; articles: RelatedLink[] }) {
  if (!articles.length) return null;
  return (
    <section className="mt-12">
      <h2 className="text-xl font-extrabold">{t("relatedArticles", lang)}</h2>
      <ul className="mt-4 grid gap-3 sm:grid-cols-2">
        {articles.map((a) => (
          <li key={a.slug}><Link className="card card-hover block p-4 font-bold" href={path(lang, "articles", a.slug)}>{a.title || a.slug}</Link></li>
        ))}
      </ul>
    </section>
  );
}
