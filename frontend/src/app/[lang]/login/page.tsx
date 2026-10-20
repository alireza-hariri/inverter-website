import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { isLang, path, t, type Lang } from "@/lib/i18n";
import Breadcrumbs from "@/components/breadcrumbs";
import { OtpRequestForm } from "@/components/otp-login-form";
export const dynamic = "force-dynamic";
// Account pages have nothing for a search engine and must not compete for the brand name.
export const metadata: Metadata = { title: { absolute: "ورود | Sign in" }, robots: { index: false, follow: false } };
export default async function LoginPage({ params }: { params: Promise<{ lang: string }> }) {
  const { lang } = await params;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  return (
    <main className="container-x py-10 max-w-lg">
      <Breadcrumbs items={[{ label: t("home", l), href: path(l) }, { label: t("login", l) }]} />
      <h1 className="mt-4 text-2xl font-black">{t("login", l)}</h1>
      <div className="mt-5"><OtpRequestForm lang={l} /></div>
    </main>
  );
}
