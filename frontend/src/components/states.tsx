import type { Lang } from "@/lib/i18n";
import { t } from "@/lib/i18n";

export function EmptyState({ lang, query }: { lang: Lang; query?: string }) {
  return (
    <div className="card p-10 text-center">
      <div className="text-4xl">🔍</div>
      <p className="mt-3 font-bold">{t("noResults", lang)}</p>
      {query ? <p className="mt-1 text-sm text-slate-500">«{query}»</p> : null}
    </div>
  );
}

export function ErrorState({ lang, message, onRetry }: { lang: Lang; message?: string; onRetry?: () => void }) {
  return (
    <div className="card p-10 text-center">
      <p className="font-extrabold text-lg">{t("errorTitle", lang)}</p>
      <p className="mt-2 text-sm text-slate-500">{message || t("errorText", lang)}</p>
      {onRetry ? <button className="btn-gold mt-5" onClick={onRetry}>{t("retry", lang)}</button> : null}
    </div>
  );
}

export function Skeletons({ n = 3 }: { n?: number }) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      {Array.from({ length: n }).map((_, i) => (
        <div key={i} className="card p-5 space-y-3"><div className="skel h-5 w-2/3" /><div className="skel h-20" /><div className="skel h-4 w-1/3" /></div>
      ))}
    </div>
  );
}

export function JsonLd({ data }: { data: unknown }) {
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }} />;
}
