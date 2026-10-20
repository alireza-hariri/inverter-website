import Link from "next/link";
import type { Lang } from "@/lib/i18n";
import { path, t } from "@/lib/i18n";
import type { HomeSite } from "@/types/content";

const SERVICE_LINKS: [string, string, string][] = [
  ["elevator-inverter-repair", "تعمیر اینورتر آسانسور", "Elevator inverter repair"],
  ["industrial-inverter-repair", "تعمیر اینورتر صنعتی", "Industrial inverter repair"],
  ["welding-inverter-repair", "تعمیر اینورتر دستگاه جوش", "Welding machine inverter repair"],
  ["cooler-inverter-repair", "تعمیر اینورتر کولر", "Cooler inverter repair"],
  ["solar-inverter-repair", "تعمیر سانورتر خورشیدی", "Solar inverter repair"],
];

export default function SiteFooter({ lang, site, siteTitle }: { lang: Lang; site: HomeSite | null; siteTitle: string }) {
  const fa = lang === "fa";
  return (
    <footer className="mt-20 bg-[#0b1530] pb-20 text-slate-300 md:pb-0">
      <div className="container-x grid gap-10 py-14 md:grid-cols-[1.4fr_1fr_1fr_1.2fr]">
        <div>
          <div className="flex items-center gap-2 text-xl font-extrabold text-white">
            <span className="logo-mark" aria-hidden="true">EG</span>{siteTitle}
          </div>
          <p className="mt-3 text-sm leading-7 opacity-80">
            {site?.tagline || (fa ? "عیب‌یابی، تعمیرات و نگهداری اینورترهای آسانسوری، صنعتی و خورشیدی." : "Troubleshooting, repair and maintenance of elevator, industrial and solar inverters.")}
          </p>
        </div>
        <nav aria-label={t("services", lang)}>
          <div className="footer-title">{t("services", lang)}</div>
          {SERVICE_LINKS.map(([slug, faLabel, enLabel]) => (
            <Link key={slug} className="footer-link" href={path(lang, "services", slug)}>{fa ? faLabel : enLabel}</Link>
          ))}
        </nav>
        <nav aria-label={fa ? "دسترسی سریع" : "Quick links"}>
          <div className="footer-title">{fa ? "دسترسی سریع" : "Quick links"}</div>
          {(["brands", "articles", "about", "contact"] as const).map((s) => (
            <Link key={s} className="footer-link" href={path(lang, s)}>{t(s, lang)}</Link>
          ))}
        </nav>
        <address className="not-italic">
          <div className="footer-title">{t("contact", lang)}</div>
          {site?.phone ? <a className="footer-link text-lg font-bold text-white" dir="ltr" href={"tel:" + site.phone.replace(/\s/g, "")}>{site.phone}</a> : null}
          {site?.email ? <a className="footer-link" href={`mailto:${site.email}`}>{site.email}</a> : null}
          {site?.address ? <p className="mt-2 text-sm leading-7 opacity-80">{site.address}</p> : null}
          {site?.opening_hours_text ? <p className="mt-1 text-sm opacity-80">{site.opening_hours_text}</p> : null}
        </address>
      </div>
      <div className="border-t border-white/10 py-5 text-center text-xs opacity-70">© {new Date().getFullYear()} {siteTitle}</div>
    </footer>
  );
}
