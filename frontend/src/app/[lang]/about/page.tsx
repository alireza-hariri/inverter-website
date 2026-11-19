import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getHome, getSeoSettings } from "@/lib/content-api";
import { buildMeta } from "@/lib/seo";
import { isLang, path, t, type Lang } from "@/lib/i18n";
import Breadcrumbs from "@/components/breadcrumbs";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ lang: string }> }): Promise<Metadata> {
  const { lang } = await params;
  if (!isLang(lang)) return {};
  const settings = await getSeoSettings(lang).catch(() => null);
  return buildMeta(lang, settings, { title: lang === "fa" ? "درباره ما" : "About us", pathParts: ["about"], page: settings?.pages.about });
}

export default async function AboutPage({ params }: { params: Promise<{ lang: string }> }) {
  const { lang } = await params;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const fa = l === "fa";
  const home = await getHome(l).catch(() => null);
  const address = fa
    ? "تهران، پاسداران، میدان فرخی یزدی، پلاک ۶، واحد ۶"
    : "Unit 6, No. 6, Farrokhi Yazdi Square, Pasdaran, Tehran, Iran";
  const mapUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
  const feats: { h: string; s: string }[] = fa
    ? [
        { h: "عیب‌یابی تخصصی", s: "برد قدرت، برد کنترل، IGBT و خازن‌ها با گزارش شفاف عیب" },
        { h: "تعمیرات", s: "تعمیر در سطح قطعه با تست کامل زیر بار و گارانتی خدمات" },
        { h: "نگهداری", s: "سرویس دوره‌ای، پایش وضعیت و پشتیبانی نصب و راه‌اندازی" },
      ]
    : [
        { h: "Diagnostics", s: "Power and control boards, IGBTs and capacitors with clear fault reports" },
        { h: "Repair", s: "Component-level repair with full load testing and warranty" },
        { h: "Maintenance", s: "Periodic service, condition monitoring and commissioning support" },
      ];
  const processSteps: { h: string; s: string }[] = fa
    ? [
        { h: "بررسی اولیه", s: "شرح علائم، کد خطا و شرایط بروز مشکل را از شما می‌گیریم." },
        { h: "عیب‌یابی و اعلام نتیجه", s: "بخش‌های مرتبط بررسی می‌شوند و نتیجه و هزینه پیشنهادی شفاف اعلام می‌شود." },
        { h: "تعمیر و تست", s: "پس از تأیید شما، تعمیر انجام و عملکرد دستگاه پیش از تحویل بررسی می‌شود." },
      ]
    : [
        { h: "Initial review", s: "We collect the symptoms, fault codes and operating conditions." },
        { h: "Diagnosis and report", s: "We inspect the relevant components and clearly share findings and the estimate." },
        { h: "Repair and testing", s: "After approval, we repair the drive and check its operation before delivery." },
      ];
  return (
    <main className="container-x py-10">
      <Breadcrumbs items={[{ label: t("home", l), href: path(l) }, { label: t("about", l) }]} />

      <section className="hero mt-5 rounded-[1.75rem]">
        <div className="hero__grid" aria-hidden="true" />
        <div className="relative grid items-center gap-8 p-6 md:grid-cols-[1.15fr_0.85fr] md:p-10 lg:gap-14">
          <div>
            <span className="hero__eyebrow">{fa ? "عیب‌یابی • تعمیرات • نگهداری" : "Troubleshooting • Repair • Maintenance"}</span>
            <h1 className="hero__title mt-5">
              {fa ? "عیب‌یابی دقیق، پیش از هر تصمیم برای تعمیر" : "Accurate diagnostics before every repair decision"}
            </h1>
            <p className="mt-4 max-w-xl leading-8 text-white/75">
              {fa
                ? "الکتروگلد در زمینه عیب‌یابی، تعمیر و نگهداری درایوهای آسانسوری، صنعتی و خورشیدی فعالیت می‌کند. تلاش ما این است که علت خرابی و راهکار پیشنهادی را روشن و قابل‌فهم با شما در میان بگذاریم."
                : "ElectroGold provides troubleshooting, repair and maintenance for elevator, industrial and solar drives. We aim to explain the cause of a fault and the recommended solution clearly."}
            </p>
            <Link href={path(l, "contact")} className="btn-gold btn-lg mt-6 inline-block">{t("requestService", l)}</Link>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-5 shadow-2xl md:p-7" aria-hidden="true">
            <div className="flex items-center justify-between gap-3 border-b border-dashed border-white/15 pb-4">
              <div>
                <div className="text-xs font-bold text-white/55">{fa ? "رویکرد فنی الکتروگلد" : "ElectroGold technical approach"}</div>
                <div className="mt-1 font-extrabold text-white">{fa ? "از بررسی تا اطمینان از عملکرد" : "From inspection to functional checks"}</div>
              </div>
              <span className="grid size-11 shrink-0 place-items-center rounded-xl bg-amber-300/15 text-xl text-amber-300">⌁</span>
            </div>
            <svg viewBox="0 0 520 150" className="mt-5 h-auto w-full" fill="none" role="presentation">
              <path d="M8 112h86l30-2 20-49 26 76 28-99 28 77 24-39 20 34 22-1 25-55 25 57h32l28-3 31 2 26-3" stroke="#f5cf5e" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M8 133h504" stroke="white" strokeOpacity=".2" strokeWidth="2" strokeDasharray="6 8" />
              <circle cx="164" cy="137" r="6" fill="#f5cf5e" />
              <circle cx="327" cy="137" r="6" fill="#f5cf5e" />
              <circle cx="475" cy="137" r="6" fill="#f5cf5e" />
            </svg>
            <div className="mt-3 grid grid-cols-3 gap-2 text-center text-xs font-semibold leading-5 text-white/65">
              <span>{fa ? "بررسی" : "Inspect"}</span>
              <span>{fa ? "عیب‌یابی" : "Diagnose"}</span>
              <span>{fa ? "تست عملکرد" : "Test"}</span>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-10 max-w-4xl">
        <span className="eyebrow">{fa ? "درباره مجموعه" : "About us"}</span>
        <h2 className="text-2xl font-black">{fa ? `الکتروگلد؛ همراه فنی تجهیزات شما` : "ElectroGold: technical support for your equipment"}</h2>
        <p className="mt-3 leading-8 text-slate-600">
          {fa
            ? "خدمات ما برندهایی مانند یاسکاوا، مونارک، اچ‌پی‌مونت، زیلابگ، دلتا، اینوونس و سانورترهای گرووات را پوشش می‌دهد. در فرایند تعمیر، بخش‌های مرتبط با مدار قدرت و کنترل بررسی می‌شوند و پس از تأیید مشتری، دستگاه تعمیر و پیش از تحویل از نظر عملکرد آزمایش می‌شود. گزارش شفاف عیب، تست زیر بار و گارانتی خدمات از اصول کاری ماست."
            : "Our services cover brands including Yaskawa, Monarch, HPMont, Zilabeg, Delta, Inovance and Growatt solar inverters. We inspect the relevant power and control circuits, share our findings, and proceed with repairs after approval. Functional checks, load testing and a service warranty are core parts of our work."}
        </p>
      </section>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        {feats.map((f) => (
          <div key={f.h} className="card card-hover p-6">
            <span className="mb-4 grid size-11 place-items-center rounded-xl bg-amber-50 text-xl font-black text-amber-700" aria-hidden="true">✓</span>
            <h3 className="font-extrabold">{f.h}</h3>
            <p className="mt-2 text-sm text-slate-500 leading-7">{f.s}</p>
          </div>
        ))}
      </div>

      <section className="process mt-10">
        <span className="eyebrow">{fa ? "روشن و مرحله‌به‌مرحله" : "Clear, step by step"}</span>
        <h2 className="text-2xl font-black">{fa ? "فرایند همکاری با الکتروگلد" : "How we work"}</h2>
        <ol className="mt-6 grid gap-4 md:grid-cols-3">
          {processSteps.map((step, i) => (
            <li key={step.h} className="process__step">
              <span className="process__num" aria-hidden="true">{fa ? "۱۲۳"[i] : i + 1}</span>
              <h3 className="mt-4 font-extrabold">{step.h}</h3>
              <p className="mt-2 text-sm leading-7 text-white/65">{step.s}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="card mt-8 grid gap-5 p-6 md:grid-cols-[1fr_auto] md:items-center md:p-8">
        <div>
          <span className="eyebrow">{fa ? "موقعیت مکانی" : "Location"}</span>
          <h2 className="text-xl font-black">{fa ? "نشانی الکتروگلد" : "Visit ElectroGold"}</h2>
          <p className="mt-2 leading-8 text-slate-600">{address}</p>
          {home?.site.phone ? <p className="mt-1 text-sm text-slate-600">{t("phone", l)}: <a className="font-bold text-slate-900" dir="ltr" href={"tel:" + home.site.phone.replace(/\s/g, "")}>{home.site.phone}</a></p> : null}
          {home?.site.mobile ? <p className="mt-1 text-sm text-slate-600">{t("mobile", l)}: <a className="font-bold text-slate-900" dir="ltr" href={"tel:" + home.site.mobile.replace(/\s/g, "")}>{home.site.mobile}</a></p> : null}
        </div>
        <a className="btn-dark text-center" href={mapUrl} target="_blank" rel="noreferrer">
          {fa ? "مشاهده روی نقشه ↗" : "View on map ↗"}
        </a>
      </section>

      <div className="cta-band mt-8">
        <div>
          <h2 className="text-xl font-black">{fa ? "برای بررسی دستگاهتان راهنمایی می‌خواهید؟" : "Need help assessing your drive?"}</h2>
          <p className="mt-1 text-sm text-slate-800/75">{fa ? "علائم یا کد خطا را برای کارشناسان ما بفرستید." : "Share the symptoms or fault code with our team."}</p>
        </div>
        <Link href={path(l, "contact")} className="btn-dark">{fa ? "درخواست مشاوره" : "Request a consultation"}</Link>
      </div>
    </main>
  );
}
