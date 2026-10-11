import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getHome, getServices } from "@/lib/content-api";
import { metaFor } from "@/lib/seo";
import { isLang, path, t, type Lang } from "@/lib/i18n";
import Breadcrumbs from "@/components/breadcrumbs";
import ContactInquiryForm from "@/components/contact-inquiry-form";
export const dynamic = "force-dynamic";
export async function generateMetadata({ params }: { params: Promise<{ lang: string }> }): Promise<Metadata> {
  const { lang } = await params;
  if (!isLang(lang)) return {};
  return metaFor(lang, { title: lang === "fa" ? "تماس و درخواست تعمیر | الکتروگلد" : "Contact & repair request | ElectroGold", pathParts: ["contact"] });
}
export default async function ContactPage({ params }: { params: Promise<{ lang: string }> }) {
  const { lang } = await params;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const [home, services] = await Promise.all([getHome(l).catch(() => null), getServices(l).catch(() => null)]);
  return (
    <main className="container-x py-10">
      <Breadcrumbs items={[{ label: t("home", l), href: path(l) }, { label: t("contact", l) }]} />
      <h1 className="mt-4 text-3xl font-black">{t("contact", l)}</h1>
      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <ContactInquiryForm lang={l} services={(services?.results ?? []).map((s) => ({ slug: s.slug, title: s.title }))} />
        <div className="space-y-4">
          <div className="card p-6 leading-8 text-sm">
            {home?.site.phone ? <div><b>{t("phone", l)}:</b> <a dir="ltr" href={"tel:" + home.site.phone.replace(/\s/g, "")}>{home.site.phone}</a></div> : null}
            {home?.site.address ? <div className="mt-2"><b>{t("address", l)}:</b> {home.site.address}</div> : null}
            {!home?.site.phone && !home?.site.address ? <p className="text-slate-500">{l === "fa" ? "برای ثبت درخواست، فرم روبه‌رو را تکمیل کنید." : "Fill in the form to submit your request."}</p> : null}
          </div>
          <div className="card p-6 text-sm text-slate-500 leading-7">{l === "fa" ? "ساعت پاسخگویی: شنبه تا پنجشنبه، ۸ تا ۱۸. برای خرابی‌های اضطراری آسانسور در پیام ذکر کنید." : "Working hours: Sat–Thu, 8–18. Mention elevator emergencies in your message."}</div>
        </div>
      </div>
    </main>
  );
}
