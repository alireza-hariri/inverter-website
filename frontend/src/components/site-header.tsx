import Link from "next/link";
import type { Lang } from "@/lib/i18n";
import { path, t } from "@/lib/i18n";
import LanguageSwitcher from "./language-switcher";
import MobileMenu from "./mobile-menu";

export default function SiteHeader({ lang, phone }: { lang: Lang; phone?: string }) {
  const links = [
    { href: path(lang, "services"), label: t("services", lang) },
    { href: path(lang, "brands"), label: t("brands", lang) },
    { href: path(lang, "articles"), label: t("articles", lang) },
    { href: path(lang, "about"), label: t("about", lang) },
    { href: path(lang, "contact"), label: t("contact", lang) },
  ];
  return (
    <header className="site-header sticky top-0 z-40 text-white">
      <div className="container-x flex items-center gap-4 py-3">
        <Link href={path(lang)} className="flex items-center gap-2 font-extrabold text-xl">
          <span className="logo-mark" aria-hidden="true">EG</span>
          <span>{lang === "fa" ? "الکتروگلد" : "ElectroGold"}</span>
        </Link>
        <nav className="hidden md:flex items-center gap-5 ms-6 text-sm" aria-label="main">
          {links.map((l) => (
            <Link key={l.href} href={l.href} className="opacity-90 hover:opacity-100 hover:text-[#f5cf5e]">{l.label}</Link>
          ))}
        </nav>
        <div className="ms-auto flex items-center gap-3">
          {phone ? <a href={`tel:${phone.replace(/\s/g, "")}`} className="hidden lg:inline-flex items-center gap-1.5 text-sm font-bold text-[#f5cf5e]" dir="ltr"><span aria-hidden="true">☎</span>{phone}</a> : null}
          <LanguageSwitcher lang={lang} />
          <Link href={path(lang, "contact")} className="btn-gold hidden sm:inline-block !py-2 !px-4 text-sm">{t("requestService", lang)}</Link>
          <MobileMenu lang={lang} links={links} />
        </div>
      </div>
    </header>
  );
}
