import Link from "next/link";
import type { Lang } from "@/lib/i18n";
import { path, t } from "@/lib/i18n";

export default function Hero({ lang, title, tagline }: { lang: Lang; title: string; tagline?: string }) {
  return (
    <section className="hero-bg text-white">
      <div className="container-x py-16 md:py-24 grid gap-10 md:grid-cols-2 items-center">
        <div>
          <span className="chip">{lang === "fa" ? "عیب‌یابی • تعمیرات • نگهداری" : "Troubleshooting • Repair • Maintenance"}</span>
          <h1 className="mt-4 text-3xl md:text-5xl font-black leading-tight">{title}</h1>
          {tagline ? <p className="mt-4 text-white/80 text-lg leading-8">{tagline}</p> : null}
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href={path(lang, "contact")} className="btn-gold">{t("requestService", lang)}</Link>
            <Link href={path(lang, "services")} className="btn-ghost !bg-transparent !text-white !border-white/30">{t("services", lang)}</Link>
          </div>
          <div className="mt-8 grid grid-cols-3 gap-3 text-center text-sm">
            {[
              lang === "fa" ? ["آسانسوری", "یاسکاوا، مونارک، اچ‌پی‌مونت، زیلابگ"] : ["Elevator", "Yaskawa, Monarch, HPMont, Zilabeg"],
              lang === "fa" ? ["صنعتی", "دلتا، یاسکاوا، اینوونس"] : ["Industrial", "Delta, Yaskawa, Inovance"],
              lang === "fa" ? ["خورشیدی", "گرووات"] : ["Solar", "Growatt"],
            ].map(([h, s]) => (
              <div key={h} className="rounded-xl border border-white/15 bg-white/5 p-3">
                <div className="font-extrabold text-[#f5cf5e]">{h}</div>
                <div className="mt-1 text-xs text-white/70">{s}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="hidden md:block">
          <div className="card !bg-white/5 !border-white/15 p-8 text-white/85 leading-8">
            <div className="text-6xl font-black text-[#e8b62a]" dir="ltr">AC / DC</div>
            <p className="mt-4">{lang === "fa" ? "تعمیر تخصصی درایو و اینورتر با تست کامل زیر بار، گزارش عیب‌یابی و گارانتی خدمات." : "Specialist drive and inverter repair with full load testing, fault reports and service warranty."}</p>
            <ul className="mt-4 space-y-2 text-sm">
              {(lang === "fa" ? ["عیب‌یابی برد قدرت و کنترل", "تعویض IGBT و خازن‌ها", "سرویس دوره‌ای و نگهداری", "پشتیبانی نصب و راه‌اندازی"] : ["Power & control board diagnostics", "IGBT and capacitor replacement", "Periodic service & maintenance", "Installation & commissioning support"]).map((x) => (
                <li key={x}>✓ {x}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
