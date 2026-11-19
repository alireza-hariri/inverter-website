import Link from "next/link";
import type { Lang } from "@/lib/i18n";
import { path, t } from "@/lib/i18n";
import LanguageSwitcher from "./language-switcher";
import MobileMenu from "./mobile-menu";
import BrandLogo from "./brand-logo";

export default function SiteHeader({ lang, phone, mobile }: { lang: Lang; phone?: string; mobile?: string }) {
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
        <Link href={path(lang)} className="flex shrink-0 items-center" aria-label={lang === "fa" ? "صفحه اصلی الکتروگلد" : "ElectroGold home"}>
          <BrandLogo lang={lang} />
        </Link>
        <nav className="hidden md:flex items-center gap-5 ms-6 text-sm" aria-label="main">
          {links.map((l) => (
            <Link key={l.href} href={l.href} className="opacity-90 hover:opacity-100 hover:text-[#f5cf5e]">{l.label}</Link>
          ))}
        </nav>
        <div className="ms-auto flex items-center gap-3">
          {phone || mobile ? (
            <div className="hidden 2xl:flex flex-col items-start text-xs font-bold leading-5 text-[#f5cf5e]">
              {phone ? <a href={`tel:${phone.replace(/\s/g, "")}`} title={t("phone", lang)} dir="ltr"><span aria-hidden="true">☎ </span>{phone}</a> : null}
              {mobile ? <a href={`tel:${mobile.replace(/\s/g, "")}`} title={t("mobile", lang)} dir="ltr"><span aria-hidden="true">📱 </span>{mobile}</a> : null}
            </div>
          ) : null}
          <LanguageSwitcher lang={lang} />
          <Link href={path(lang, "contact")} className="btn-gold hidden sm:inline-block !py-2 !px-4 text-sm">{t("requestService", lang)}</Link>
          <MobileMenu lang={lang} links={links} />
        </div>
      </div>
    </header>
  );
}
