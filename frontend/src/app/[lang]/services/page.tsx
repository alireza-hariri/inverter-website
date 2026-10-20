import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { getSeoSettings, getServices } from "@/lib/content-api";
import { buildMeta } from "@/lib/seo";
import { isLang, path, t, type Lang } from "@/lib/i18n";
import Breadcrumbs from "@/components/breadcrumbs";
import { ServiceCard } from "@/components/cards";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ lang: string }> }): Promise<Metadata> {
  const { lang } = await params;
  if (!isLang(lang)) return {};
  const settings = await getSeoSettings(lang).catch(() => null);
  return buildMeta(lang, settings, { title: lang === "fa" ? "خدمات تعمیر اینورتر" : "Inverter repair services", pathParts: ["services"], page: settings?.pages.services });
}

export default async function ServicesPage({ params }: { params: Promise<{ lang: string }> }) {
  const { lang } = await params;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const [page, settings] = await Promise.all([getServices(l), getSeoSettings(l).catch(() => null)]);
  const intro = settings?.pages.services?.intro;
  return (
    <main className="container-x py-10">
      <Breadcrumbs items={[{ label: t("home", l), href: path(l) }, { label: t("services", l) }]} />
      <h1 className="mt-4 text-3xl font-black">{t("services", l)}</h1>
      <p className="mt-2 max-w-3xl leading-8 text-slate-500">{intro || (l === "fa" ? "عیب‌یابی، تعمیرات و نگهداری اینورترهای آسانسوری، صنعتی و خورشیدی." : "Troubleshooting, repair and maintenance of elevator, industrial and solar inverters.")}</p>
      {page.results.length === 0 ? (
        <div className="card mt-6 p-10 text-center"><p className="font-bold">{t("noResults", l)}</p><Link className="btn-gold mt-4 inline-block" href={path(l, "contact")}>{t("contact", l)}</Link></div>
      ) : (
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{page.results.map((s) => (<ServiceCard key={s.slug} lang={l} s={s} />))}</div>
      )}
    </main>
  );
}
