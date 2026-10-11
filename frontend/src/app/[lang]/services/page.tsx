import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { getServices } from "@/lib/content-api";
import { metaFor } from "@/lib/seo";
import { isLang, path, t, type Lang } from "@/lib/i18n";
import Breadcrumbs from "@/components/breadcrumbs";
import { ServiceCard } from "@/components/cards";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ lang: string }> }): Promise<Metadata> {
  const { lang } = await params;
  if (!isLang(lang)) return {};
  return metaFor(lang, { title: lang === "fa" ? "خدمات تعمیر اینورتر | الکتروگلد" : "Inverter repair services | ElectroGold", pathParts: ["services"] });
}

export default async function ServicesPage({ params }: { params: Promise<{ lang: string }> }) {
  const { lang } = await params;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const page = await getServices(l).catch(() => null);
  return (
    <main className="container-x py-10">
      <Breadcrumbs items={[{ label: t("home", l), href: path(l) }, { label: t("services", l) }]} />
      <h1 className="mt-4 text-3xl font-black">{t("services", l)}</h1>
      <p className="mt-2 text-slate-500">{l === "fa" ? "عیب‌یابی، تعمیرات و نگهداری اینورترهای آسانسوری، صنعتی و خورشیدی." : "Troubleshooting, repair and maintenance of elevator, industrial and solar inverters."}</p>
      {!page || page.results.length === 0 ? (
        <div className="card mt-6 p-10 text-center"><p className="font-bold">{t("noResults", l)}</p><Link className="btn-gold mt-4 inline-block" href={path(l, "contact")}>{t("contact", l)}</Link></div>
      ) : (
        <div className="mt-6 grid gap-4 md:grid-cols-3">{page.results.map((s) => (<ServiceCard key={s.slug} lang={l} s={s} />))}</div>
      )}
    </main>
  );
}
