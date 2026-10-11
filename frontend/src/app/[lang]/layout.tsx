import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { Lang } from "@/lib/i18n";
import { dirOf, isLang } from "@/lib/i18n";
import { getHome } from "@/lib/content-api";
import SiteHeader from "@/components/site-header";
import SiteFooter from "@/components/site-footer";

export const dynamic = "force-dynamic";

export async function generateStaticParams() {
  return [{ lang: "fa" }, { lang: "en" }];
}

export async function generateMetadata({ params }: { params: Promise<{ lang: string }> }): Promise<Metadata> {
  const { lang } = await params;
  if (!isLang(lang)) return {};
  try {
    const home = await getHome(lang);
    return {
      title: home.site.site_title,
      description: home.site.meta_description || home.site.tagline,
    };
  } catch {
    return { title: lang === "fa" ? "الکتروگلد" : "ElectroGold" };
  }
}

export default async function LangLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ lang: string }>;
}) {
  const { lang } = await params;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  let phone = "";
  let address = "";
  let siteTitle = l === "fa" ? "الکتروگلد" : "ElectroGold";
  try {
    const home = await getHome(l);
    phone = home.site.phone;
    address = home.site.address;
    siteTitle = home.site.site_title || siteTitle;
  } catch {
    /* header/footer render with defaults */
  }
  return (
    <div dir={dirOf(l)} lang={l} className="flex flex-1 flex-col">
      <SiteHeader lang={l} phone={phone} />
      <div className="flex-1">{children}</div>
      <SiteFooter lang={l} phone={phone} address={address} siteTitle={siteTitle} />
    </div>
  );
}
