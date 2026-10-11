import Link from "next/link";
export default function Breadcrumbs({ items }: { items: { label: string; href?: string }[] }) {
  return (
    <nav aria-label="breadcrumb" className="text-sm text-slate-500">
      <ol itemScope itemType="https://schema.org/BreadcrumbList" className="flex flex-wrap gap-1.5">
        {items.map((it, i) => (
          <li key={i} itemProp="itemListElement" itemScope itemType="https://schema.org/ListItem" className="flex gap-1.5 items-center">
            <meta itemProp="position" content={String(i + 1)} />
            {it.href ? <Link itemProp="item" href={it.href} className="hover:text-slate-800"><span itemProp="name">{it.label}</span></Link> : <span itemProp="name">{it.label}</span>}
            {i < items.length - 1 ? <span aria-hidden="true">/</span> : null}
          </li>
        ))}
      </ol>
    </nav>
  );
}
