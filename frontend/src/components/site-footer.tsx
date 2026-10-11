import Link from "next/link";
import type { Lang } from "@/lib/i18n";
import { path, t } from "@/lib/i18n";
export default function SiteFooter({ lang, phone, address, siteTitle }: { lang: Lang; phone?: string; address?: string; siteTitle: string }) {
  return (
    <footer className="mt-16 text-slate-200" style={{ background: "#0b1530" }}>
      <div className="container-x grid gap-8 py-12 md:grid-cols-4">
        <div>
          <div className="font-extrabold text-xl text-white">{siteTitle}</div>
          <p className="mt-2 text-sm opacity-80">{lang === "fa" ? "عیب‌یابی، تعمیرات و نگهداری اینورترهای آسانسوری، صنعتی و خورشیدی." : "Troubleshooting, repair and maintenance of elevator, industrial and solar inverters."}</p>
        </div>
        <div>
          <div className="font-bold text-white mb-3">{t("services", lang)}</div>
          {[["elevator-inverter-repair", lang === "fa" ? "تعمیر اینورتر آسانسوری" : "Elevator inverter repair"],["industrial-inverter-repair", lang === "fa" ? "تعمیر اینورتر صنعتی" : "Industrial inverter repair"],["welding-inverter-repair", lang === "fa" ? "تعمیر اینورتر دستگاه جوش" : "Welding machine inverter repair"],["cooler-inverter-repair", lang === "fa" ? "تعمیر اینورتر کولر" : "Cooler inverter repair"],["solar-inverter-repair", lang === "fa" ? "تعمیر سانورتر خورشیدی" : "Solar inverter repair"]].map(([s, l]) => (
            <div key={s}><Link className="text-sm opacity-80 hover:opacity-100" href={path(lang, "services", s)}>{l}</Link></div>
          ))}
        </div>
        <div>
          <div className="font-bold text-white mb-3">{lang === "fa" ? "دسترسی سریع" : "Quick links"}</div>
          {[["brands", t("brands", lang)],["articles", t("articles", lang)],["about", t("about", lang)],["contact", t("contact", lang)]].map(([s, l]) => (
            <div key={s}><Link className="text-sm opacity-80 hover:opacity-100" href={path(lang, s)}>{l}</Link></div>
          ))}
        </div>
        <div>
          <div className="font-bold text-white mb-3">{t("contact", lang)}</div>
          {phone ? <div className="text-sm"><a href={"tel:"+phone.replace(/\s/g, "")} dir="ltr">{phone}</a></div> : null}
          {address ? <div className="text-sm opacity-80 mt-1">{address}</div> : null}
        </div>
      </div>
      <div className="border-t border-white/10 py-4 text-center text-xs opacity-70">© {new Date().getFullYear()} {siteTitle}</div>
    </footer>
  );
}
