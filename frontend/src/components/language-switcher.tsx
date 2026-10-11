"use client";
import { usePathname } from "next/navigation";
import Link from "next/link";
import type { Lang } from "@/lib/i18n";
import { otherLang, switchPath } from "@/lib/i18n";
export default function LanguageSwitcher({ lang }: { lang: Lang }) {
  const pathname = usePathname() || `/`;
  const other = otherLang(lang);
  return (
    <Link href={switchPath(pathname, other)} className="rounded-lg border border-white/25 px-3 py-1.5 text-sm font-bold hover:bg-white/10" lang={other}>
      {other === "fa" ? "فارسی" : "EN"}
    </Link>
  );
}
