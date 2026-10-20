import Link from "next/link";
import type { Lang } from "@/lib/i18n";
import { path, t } from "@/lib/i18n";

/** On phones, calling is the conversion: keep Call / Request repair one tap away. */
export default function MobileCtaBar({ lang, phone, whatsapp }: { lang: Lang; phone: string; whatsapp: string }) {
  const fa = lang === "fa";
  return (
    <div className="mobile-cta md:hidden">
      {phone ? <a href={`tel:${phone.replace(/\s/g, "")}`} className="mobile-cta__btn">📞 {fa ? "تماس فوری" : "Call now"}</a> : null}
      {whatsapp ? <a href={`https://wa.me/${whatsapp.replace(/\D/g, "")}`} className="mobile-cta__btn" rel="noopener" target="_blank">{fa ? "واتساپ" : "WhatsApp"}</a> : null}
      <Link href={path(lang, "contact")} className="mobile-cta__btn mobile-cta__btn--gold">{t("requestService", lang)}</Link>
    </div>
  );
}
