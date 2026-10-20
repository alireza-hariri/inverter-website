import Link from "next/link";
import type { Lang } from "@/lib/i18n";
import { path, t } from "@/lib/i18n";
import type { TocEntry } from "@/types/content";
import { TableOfContents } from "./rich-body";

/** The sticky column beside a long page: contents, then the call to action. */
export default function DetailSidebar({ lang, toc, phone, children }: {
  lang: Lang; toc: TocEntry[]; phone?: string; children?: React.ReactNode;
}) {
  const fa = lang === "fa";
  return (
    <aside className="space-y-5 lg:sticky lg:top-24 lg:self-start">
      <TableOfContents toc={toc} title={fa ? "فهرست مطالب" : "On this page"} />
      <div className="card overflow-hidden">
        <div className="bg-[#0b1530] p-5 text-white">
          <div className="text-lg font-extrabold">{t("contactCta", lang)}</div>
          <p className="mt-1 text-sm text-white/70">{fa ? "عیب‌یابی و اعلام هزینه پیش از شروع تعمیر." : "Diagnostics and a quote before any repair starts."}</p>
        </div>
        <div className="space-y-2 p-5">
          {phone ? <a href={`tel:${phone.replace(/\s/g, "")}`} className="btn-dark block text-center" dir="ltr">☎ {phone}</a> : null}
          <Link href={path(lang, "contact")} className="btn-gold block text-center">{t("requestService", lang)}</Link>
        </div>
      </div>
      {children}
    </aside>
  );
}
