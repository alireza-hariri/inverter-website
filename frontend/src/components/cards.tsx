import Link from "next/link";
import type { Lang } from "@/lib/i18n";
import { categoryLabel, path, t } from "@/lib/i18n";
import type { ArticleItem, BrandItem, ServiceItem } from "@/types/content";

export function SectionHeading({ title, sub, link }: { title: string; sub?: string; link?: { href: string; label: string } }) {
  return (
    <div className="flex items-end justify-between gap-4 mb-6">
      <div>
        <h2 className="text-2xl font-extrabold">{title}</h2>
        {sub ? <p className="mt-1 text-slate-500">{sub}</p> : null}
      </div>
      {link ? <Link href={link.href} className="text-sm font-bold text-[#8a6a00] hover:underline shrink-0">{link.label}</Link> : null}
    </div>
  );
}

export function ServiceCard({ lang, s }: { lang: Lang; s: ServiceItem }) {
  return (
    <Link href={path(lang, "services", s.slug)} className="card p-6 hover:shadow-lg transition-shadow block">
      <span className="chip">{categoryLabel(s.category, lang)}</span>
      <h3 className="mt-3 font-extrabold text-lg">{s.title}</h3>
      <p className="mt-2 text-sm text-slate-500 leading-7 line-clamp-3">{s.summary}</p>
      <span className="mt-4 inline-block text-sm font-bold text-[#8a6a00]">{t("readMore", lang)} ←</span>
    </Link>
  );
}

export function BrandCard({ lang, b }: { lang: Lang; b: BrandItem }) {
  return (
    <Link href={path(lang, "brands", b.slug)} className="card p-5 hover:shadow-lg transition-shadow block text-center">
      <div className="mx-auto h-12 w-12 rounded-xl flex items-center justify-center font-black text-lg" style={{ background: "#0b1530", color: "#f5cf5e" }}>
        {b.name.slice(0, 1)}
      </div>
      <h3 className="mt-3 font-extrabold" dir="ltr">{b.name}</h3>
      <div className="mt-1 text-xs text-slate-400">{categoryLabel(b.category, lang)}</div>
      <p className="mt-2 text-xs text-slate-500 leading-6 line-clamp-2">{b.description}</p>
    </Link>
  );
}

export function ArticleCard({ lang, a }: { lang: Lang; a: ArticleItem }) {
  return (
    <Link href={path(lang, "articles", a.slug)} className="card hover:shadow-lg transition-shadow block">
      <div className="h-36 flex items-center justify-center font-black text-3xl" style={{ background: "linear-gradient(135deg,#0b1530,#24407c)", color: "#f5cf5e" }} aria-hidden="true">
        {a.title.slice(0, 1)}
      </div>
      <div className="p-5">
        <h3 className="font-extrabold leading-7 line-clamp-2">{a.title}</h3>
        <p className="mt-2 text-sm text-slate-500 leading-7 line-clamp-2">{a.excerpt}</p>
        <span className="mt-3 inline-block text-sm font-bold text-[#8a6a00]">{t("readMore", lang)} ←</span>
      </div>
    </Link>
  );
}
