import Link from "next/link";
import type { Lang } from "@/lib/i18n";
import { path, t } from "@/lib/i18n";

const TRUST = {
  fa: ["تعمیر در سطح قطعه", "تست کامل زیر بار", "گزارش شفاف عیب‌یابی", "گارانتی خدمات"],
  en: ["Component-level repair", "Full load testing", "Clear fault reports", "Service warranty"],
};

/**
 * The homepage's single H1 comes from "Site identity → Homepage headline" in
 * the admin, so the SEO specialist controls the most important on-page phrase.
 */
export default function Hero({ lang, title, subtitle, phone, image }: {
  lang: Lang; title: string; subtitle?: string; phone?: string; image?: string;
}) {
  const fa = lang === "fa";
  return (
    <section className="hero">
      <div className="hero__grid" aria-hidden="true" />
      <div className="container-x relative grid items-center gap-12 py-16 md:grid-cols-[1.15fr_1fr] md:py-24">
        <div>
          <span className="hero__eyebrow">
            <span className="pulse" aria-hidden="true" />
            {fa ? "عیب‌یابی • تعمیرات • نگهداری" : "Troubleshooting • Repair • Maintenance"}
          </span>
          <h1 className="mt-5 text-[2rem] font-black leading-[1.35] md:text-5xl md:leading-[1.3]">{title}</h1>
          {subtitle ? <p className="mt-5 max-w-xl text-lg leading-9 text-white/75">{subtitle}</p> : null}
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href={path(lang, "contact")} className="btn-gold btn-lg">{t("requestService", lang)}</Link>
            {phone ? (
              <a href={`tel:${phone.replace(/\s/g, "")}`} className="btn-outline-light btn-lg">
                <span aria-hidden="true">☎</span> <span dir="ltr">{phone}</span>
              </a>
            ) : (
              <Link href={path(lang, "services")} className="btn-outline-light btn-lg">{t("services", lang)}</Link>
            )}
          </div>
          <ul className="mt-9 grid grid-cols-2 gap-x-6 gap-y-3 text-sm text-white/85 sm:max-w-md">
            {TRUST[lang].map((x) => (
              <li key={x} className="flex items-center gap-2"><span className="check" aria-hidden="true">✓</span>{x}</li>
            ))}
          </ul>
        </div>

        <div className="relative hidden md:block" aria-hidden="true">
          {image ? <img src={image} alt="" className="hero__photo" width={640} height={480} fetchPriority="high" /> : <div className="hero__photo" />}
          <div className="drive">
            <div className="drive__top">
              <span>DRIVE STATUS</span>
              <span className="drive__led" />
            </div>
            <div className="drive__screen" dir="ltr">
              <div className="drive__row"><span>OUT FREQ</span><b>50.00 Hz</b></div>
              <div className="drive__row"><span>DC BUS</span><b>540 V</b></div>
              <div className="drive__row"><span>LOAD TEST</span><b className="ok">PASS</b></div>
            </div>
            <div className="drive__bar"><span /></div>
          </div>
          <div className="hero__badge">
            <div className="text-xs text-slate-500">{fa ? "پوشش برندها" : "Brands covered"}</div>
            <div className="mt-0.5 text-sm font-extrabold text-slate-900" dir="ltr">Yaskawa · Monarch · Delta · Growatt</div>
          </div>
        </div>
      </div>
    </section>
  );
}
