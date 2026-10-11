import { Suspense } from "react";
import { notFound } from "next/navigation";
import { isLang, path, t, type Lang } from "@/lib/i18n";
import Breadcrumbs from "@/components/breadcrumbs";
import { OtpVerifyForm } from "@/components/otp-login-form";
export const dynamic = "force-dynamic";
export default async function VerifyPage({ params }: { params: Promise<{ lang: string }> }) {
  const { lang } = await params;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  return (
    <main className="container-x py-10 max-w-lg">
      <Breadcrumbs items={[{ label: t("home", l), href: path(l) }, { label: t("login", l), href: path(l, "login") }, { label: l === "fa" ? "تایید کد" : "Verify" }]} />
      <h1 className="mt-4 text-2xl font-black">{l === "fa" ? "تایید کد" : "Verify code"}</h1>
      <div className="mt-5"><Suspense fallback={<div className="skel h-40" />}><OtpVerifyForm lang={l} /></Suspense></div>
    </main>
  );
}
