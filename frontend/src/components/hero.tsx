import Link from "next/link";
import type { Lang } from "@/lib/i18n";
import { path, t } from "@/lib/i18n";

const TRUST = {
  fa: ["تعمیر در سطح قطعه", "تست کامل زیر بار", "گزارش شفاف عیب‌یابی", "گارانتی خدمات"],
  en: ["Component-level repair", "Full load testing", "Clear fault reports", "Service warranty"],
};

const REPORT = {
  fa: { title: "گزارش تعمیر", stages: ["عیب‌یابی برد قدرت", "تعویض IGBT و خازن‌ها", "کالیبراسیون برد کنترل"], load: "تست زیر بار" },
  en: { title: "Repair report", stages: ["Power board diagnostics", "IGBT & capacitor swap", "Control board calibration"], load: "Load test" },
};

const BRANDS = ["Yaskawa", "Monarch", "Delta", "Inovance", "Growatt"];

/**
 * The homepage's single H1 comes from "Site identity → Homepage headline" in
 * the admin, so the SEO specialist controls the most important on-page phrase.
 */
export default function Hero({ lang, title, subtitle, phone }: {
  lang: Lang; title: string; subtitle?: string; phone?: string;
}) {
  const fa = lang === "fa";
  const r = REPORT[lang];
  return (
    <section className="hero">
      <div className="hero__grid" aria-hidden="true" />
      <div className="container-x relative grid items-center gap-12 pt-14 pb-24 md:grid-cols-[1.2fr_1fr] md:pt-20 md:pb-32 lg:gap-16">
        <div>
          <span className="hero__eyebrow">
            <span className="pulse" aria-hidden="true" />
            {fa ? "عیب‌یابی • تعمیرات • نگهداری" : "Troubleshooting • Repair • Maintenance"}
          </span>
          <h1 className="hero__title mt-5">{title}</h1>
          {subtitle ? <p className="mt-5 max-w-xl text-base leading-8 text-white/70 md:text-lg md:leading-9">{subtitle}</p> : null}
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
          <ul className="hero__trust">
            {TRUST[lang].map((x) => (
              <li key={x}><span className="check" aria-hidden="true">✓</span>{x}</li>
            ))}
          </ul>
        </div>

        <div className="relative hidden md:block" aria-hidden="true">
          <div className="report">
            <div className="report__head">
              <div>
                <div className="report__label">{r.title}</div>
                <div className="report__device" dir="ltr">YASKAWA L1000A · 11 kW</div>
              </div>
              <span className="report__stamp">PASS</span>
            </div>
            <ul className="report__stages">
              {r.stages.map((x) => (
                <li key={x}><span className="report__tick">✓</span>{x}</li>
              ))}
            </ul>
            <div className="report__screen" dir="ltr">
              <div><span>OUT FREQ</span><b>50.00 Hz</b></div>
              <div><span>DC BUS</span><b>540 V</b></div>
              <div><span>OUT CURRENT</span><b>21.4 A</b></div>
            </div>
            <div className="report__load">
              <span>{r.load}</span>
              <span dir="ltr">100%</span>
            </div>
            <div className="report__bar"><span /></div>
          </div>
          <div className="hero__brands" dir="ltr">
            {BRANDS.map((b) => (<span key={b}>{b}</span>))}
          </div>
        </div>
      </div>
    </section>
  );
}
