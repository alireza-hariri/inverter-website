"use client";
import { useState } from "react";
import Link from "next/link";
import type { Lang } from "@/lib/i18n";
import { path, t } from "@/lib/i18n";
export default function MobileMenu({ lang, links }: { lang: Lang; links: { href: string; label: string }[] }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="md:hidden">
      <button aria-label="menu" onClick={() => setOpen(!open)} className="rounded-lg border border-white/25 px-3 py-1.5 font-bold">☰</button>
      {open ? (
        <div className="fixed inset-0 z-50 bg-black/60" onClick={() => setOpen(false)}>
          <div className="absolute end-0 top-0 h-full w-72 bg-white text-slate-900 p-5 flex flex-col gap-3" onClick={(e) => e.stopPropagation()}>
            <button className="self-end rounded border px-3 py-1" onClick={() => setOpen(false)}>✕</button>
            {links.map((l) => (<Link key={l.href} href={l.href} onClick={() => setOpen(false)} className="rounded-lg px-3 py-2 font-bold hover:bg-slate-100">{l.label}</Link>))}
            <Link href={path(lang, "contact")} onClick={() => setOpen(false)} className="btn-gold text-center mt-2">{t("requestService", lang)}</Link>
          </div>
        </div>
      ) : null}
    </div>
  );
}
