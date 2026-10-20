import type { Metadata, Viewport } from "next";
import localFont from "next/font/local";
import { headers } from "next/headers";
import { dirOf, type Lang } from "@/lib/i18n";
import { SITE_URL } from "@/lib/seo";
import "./globals.css";

const vazir = localFont({
  src: [{ path: "../../public/Vazirmatn[wght].woff2", style: "normal", weight: "100 900" }],
  display: "swap",
  variable: "--font-vazir",
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: "الکتروگلد | ElectroGold", template: "%s" },
  description: "عیب‌یابی، تعمیرات و نگهداری اینورترهای آسانسوری، صنعتی و خورشیدی — ElectroGold inverter repair and maintenance.",
  formatDetection: { telephone: false },
};

export const viewport: Viewport = {
  themeColor: "#0b1530",
  width: "device-width",
  initialScale: 1,
};

/**
 * `<html lang dir>` must match the page, or search engines and screen readers
 * treat English pages as Persian. The language segment is below this layout,
 * so src/proxy.ts passes it in as a request header.
 */
export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const lang: Lang = (await headers()).get("x-site-lang") === "en" ? "en" : "fa";
  return (
    <html lang={lang} dir={dirOf(lang)} className={`h-full ${vazir.variable}`}>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
