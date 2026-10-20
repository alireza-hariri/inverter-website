import Link from "next/link";
import { breadcrumbLd } from "@/lib/seo";
import { JsonLd } from "./states";

/** Visible breadcrumbs plus BreadcrumbList schema, which Google shows instead of the raw URL. */
export default function Breadcrumbs({ items }: { items: { label: string; href?: string }[] }) {
  return (
    <nav aria-label="breadcrumb" className="text-sm text-slate-500">
      <JsonLd data={breadcrumbLd(items)} />
      <ol className="flex flex-wrap items-center gap-1.5">
        {items.map((it, i) => (
          <li key={i} className="flex items-center gap-1.5">
            {it.href ? <Link href={it.href} className="hover:text-slate-800">{it.label}</Link> : <span aria-current="page" className="text-slate-700">{it.label}</span>}
            {i < items.length - 1 ? <span aria-hidden="true" className="text-slate-300">/</span> : null}
          </li>
        ))}
      </ol>
    </nav>
  );
}
