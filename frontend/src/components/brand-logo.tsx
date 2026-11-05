import type { Lang } from "@/lib/i18n";

export default function BrandLogo({ lang }: { lang: Lang }) {
  return (
    <span className="brand-logo" dir="ltr" aria-label={lang === "fa" ? "الکتروگلد، ElectroGold" : "ElectroGold, الکتروگلد"}>
      <svg className="brand-logo__mark" viewBox="0 0 100 100" aria-hidden="true" focusable="false">
        <path
          d="M 78 17 H 52 A 34 34 0 1 0 52 83 H 78"
          fill="none"
          stroke="currentColor"
          strokeLinecap="round"
          strokeWidth="20"
        />
        <circle cx="58" cy="50" r="10" fill="white" />
      </svg>
      <span className="brand-logo__type" aria-hidden="true">
        <span className="brand-logo__english"><span>ELECTRO</span><span>GOLD</span></span>
        <span className="brand-logo__persian" lang="fa" dir="rtl">الکتروگلد</span>
      </span>
    </span>
  );
}
