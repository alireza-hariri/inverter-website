import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const vazir = localFont({
  src: [{ path: "../../public/Vazirmatn[wght].woff2", style: "normal", weight: "100 900" }],
  display: "swap",
  variable: "--font-vazir",
});

export const metadata: Metadata = {
  title: { default: "الکتروگلد | ElectroGold", template: "%s | الکتروگلد" },
  description: "عیب‌یابی، تعمیرات و نگهداری اینورترهای آسانسوری، صنعتی و خورشیدی — ElectroGold inverter repair and maintenance.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" className={`h-full ${vazir.variable}`}>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
