import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getHome } from "@/lib/content-api";
import { metaFor } from "@/lib/seo";
import { isLang, path, t, type Lang } from "@/lib/i18n";
import Breadcrumbs from "@/components/breadcrumbs";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ lang: string }> }): Promise<Metadata> {
  const { lang } = await params;
  if (!isLang(lang)) return {};
  return metaFor(lang, {
    title: lang === "fa" ? "درباره الکتروگلد" : "About ElectroGold",
    pathParts: ["about"],
  });
}

export default async function AboutPage({ params }: { params: Promise<{ lang: string }> }) {
  const { lang } = await params;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const fa = l === "fa";
  const home = await getHome(l).catch(() => null);
  const siteTitle = home?.site.site_title ?? (fa ? "الکتروگلد" : "ElectroGold");
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
  return (
    <main className="container-x py-10">
      <Breadcrumbs items={[{ label: t("home", l), href: path(l) }, { label: t("about", l) }]} />
      <h1 className="mt-4 text-3xl font-black">{fa ? `درباره ${siteTitle}` : `About ${siteTitle}`}</h1>
      <p className="mt-3 text-slate-600 leading-8 max-w-3xl">
        {fa
          ? "الکتروگلد متخصص عیب‌یابی، تعمیرات و نگهداری اینورتر و درایوهای آسانسوری (یاسکاوا، مونارک، اچ‌پی‌مونت، زیلابگ)، صنعتی (دلتا، یاسکاوا، اینوونس) و سانورترهای خورشیدی گرووات است. تست کامل زیر بار، گزارش شفاف عیب و گارانتی خدمات از اصول کاری ماست."
          : "ElectroGold specialises in troubleshooting, repair and maintenance of elevator drives (Yaskawa, Monarch, HPMont, Zilabeg), industrial drives (Delta, Yaskawa, Inovance) and Growatt solar inverters — with full load testing, transparent fault reports and service warranty."}
      </p>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        {feats.map((f) => (
          <div key={f.h} className="card p-6">
            <h2 className="font-extrabold">{f.h}</h2>
            <p className="mt-2 text-sm text-slate-500 leading-7">{f.s}</p>
          </div>
        ))}
      </div>
      {home?.site.phone || home?.site.address ? (
        <div className="card mt-6 p-6 text-sm leading-8">
          {home?.site.phone ? <div>{t("phone", l)}: <a dir="ltr" href={"tel:" + home.site.phone.replace(/\s/g, "")}>{home.site.phone}</a></div> : null}
          {home?.site.address ? <div>{t("address", l)}: {home.site.address}</div> : null}
        </div>
      ) : null}
      <Link href={path(l, "contact")} className="btn-gold mt-6 inline-block">{t("requestService", l)}</Link>
    </main>
  );
}
