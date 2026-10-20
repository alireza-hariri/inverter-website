import type { Metadata } from "next";
import Script from "next/script";
import { notFound } from "next/navigation";
import type { Lang } from "@/lib/i18n";
import { isLang } from "@/lib/i18n";
import { getSeoSettings } from "@/lib/content-api";
import { buildMeta, organizationLd, siteName, websiteLd } from "@/lib/seo";
import SiteHeader from "@/components/site-header";
import SiteFooter from "@/components/site-footer";
import MobileCtaBar from "@/components/mobile-cta-bar";
import { JsonLd } from "@/components/states";

export const dynamic = "force-dynamic";

export async function generateStaticParams() {
  return [{ lang: "fa" }, { lang: "en" }];
}

// Tag IDs go straight into a script, so only the documented shapes are allowed.
const GTM_ID = /^GTM-[A-Z0-9]{4,12}$/;
const GA4_ID = /^G-[A-Z0-9]{4,14}$/;

export async function generateMetadata({ params }: { params: Promise<{ lang: string }> }): Promise<Metadata> {
  const { lang } = await params;
  if (!isLang(lang)) return {};
  const settings = await getSeoSettings(lang).catch(() => null);
  const v = settings?.global.verification;
  return {
    ...buildMeta(lang, settings, { title: "", page: settings?.pages.home }),
    applicationName: settings?.site.site_title,
    verification: {
      google: v?.google || undefined,
      yandex: v?.yandex || undefined,
      other: v?.bing ? { "msvalidate.01": v.bing } : undefined,
    },
  };
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
  const settings = await getSeoSettings(l).catch(() => null);
  const site = settings?.site;
  const siteTitle = siteName(l, settings);
  const gtm = settings && GTM_ID.test(settings.global.gtm_id) ? settings.global.gtm_id : "";
  const ga4 = settings && GA4_ID.test(settings.global.ga4_id) ? settings.global.ga4_id : "";
  return (
    <div className="flex flex-1 flex-col">
      <JsonLd data={organizationLd(l, settings)} />
      <JsonLd data={websiteLd(l, settings)} />
      {gtm ? (
        <Script id="gtm" strategy="afterInteractive">
          {`(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','${gtm}');`}
        </Script>
      ) : null}
      {ga4 ? (
        <>
          <Script src={`https://www.googletagmanager.com/gtag/js?id=${ga4}`} strategy="afterInteractive" />
          <Script id="ga4" strategy="afterInteractive">
            {`window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','${ga4}');`}
          </Script>
        </>
      ) : null}
      <a href="#main" className="skip-link">{l === "fa" ? "رفتن به محتوا" : "Skip to content"}</a>
      <SiteHeader lang={l} phone={site?.phone ?? ""} />
      <div id="main" className="flex-1">{children}</div>
      <SiteFooter lang={l} site={site ?? null} siteTitle={siteTitle} />
      <MobileCtaBar lang={l} phone={site?.phone ?? ""} whatsapp={site?.whatsapp ?? ""} />
    </div>
  );
}
