import type { TocEntry } from "@/types/content";

/**
 * A body written in the admin's visual editor. The HTML is sanitized by the
 * backend (apps/content/richtext.py) before it gets here, and headings carry
 * the ids the table of contents links to.
 */
export function RichBody({ html, fallback }: { html: string; fallback?: string }) {
  if (!html) return fallback ? <div className="prose-body"><p>{fallback}</p></div> : null;
  return <div className="prose-body" dangerouslySetInnerHTML={{ __html: html }} />;
}

export function TableOfContents({ toc, title }: { toc: TocEntry[]; title: string }) {
  if (toc.length < 2) return null;
  return (
    <nav className="toc card" aria-label={title}>
      <div className="toc__title">{title}</div>
      <ol>
        {toc.map((h) => (
          <li key={h.id} className={h.level === 3 ? "toc__sub" : undefined}>
            <a href={`#${encodeURIComponent(h.id)}`}>{h.text}</a>
          </li>
        ))}
      </ol>
    </nav>
  );
}
