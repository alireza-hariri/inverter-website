import Link from "next/link";
import type { Metadata } from "next";
import { headers } from "next/headers";
import NotFoundBeacon from "@/components/not-found-beacon";

export const metadata: Metadata = { title: { absolute: "صفحه پیدا نشد | Page not found" }, robots: { index: false, follow: true } };

/**
 * Every 404 a visitor sees is reported to the admin's 404 monitor (SEO → 404
 * monitor), where the SEO specialist turns broken URLs into redirects. It is
 * reported from the browser: Next renders this component speculatively as an
 * error boundary, so a server-side report here would log pages that exist.
 */
export default async function NotFound() {
  const h = await headers();
  const fa = h.get("x-site-lang") !== "en";
  return (
    <main className="container-x py-24 text-center">
      <NotFoundBeacon />
      <div className="text-7xl font-black text-[#e8b62a]" dir="ltr">404</div>
      <h1 className="mt-4 text-3xl font-extrabold">{fa ? "صفحه پیدا نشد" : "Page not found"}</h1>
      <p className="mt-3 text-slate-500">{fa ? "صفحه‌ای که دنبالش هستید وجود ندارد یا جابه‌جا شده است." : "The page you are looking for does not exist or has moved."}</p>
      <div className="mt-8 flex flex-wrap justify-center gap-3">
        <Link className="btn-gold" href={fa ? "/fa" : "/en"}>{fa ? "صفحه اصلی" : "Home"}</Link>
        <Link className="btn-ghost" href={fa ? "/fa/services" : "/en/services"}>{fa ? "خدمات" : "Services"}</Link>
        <Link className="btn-ghost" href={fa ? "/fa/contact" : "/en/contact"}>{fa ? "تماس با ما" : "Contact"}</Link>
      </div>
    </main>
  );
}
