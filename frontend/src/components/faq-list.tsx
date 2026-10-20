import type { Faq } from "@/types/content";
import { faqLd } from "@/lib/seo";
import { JsonLd } from "./states";

/**
 * Questions as native <details>, so they work without JavaScript and the
 * answers stay in the HTML that search engines read, plus FAQPage schema.
 */
export default function FaqList({ faqs, title, withSchema = true }: { faqs: Faq[]; title?: string; withSchema?: boolean }) {
  if (!faqs.length) return null;
  return (
    <section className="mt-10" aria-labelledby={title ? "faq-title" : undefined}>
      {title ? <h2 id="faq-title" className="text-2xl font-black">{title}</h2> : null}
      {withSchema ? <JsonLd data={faqLd(faqs)} /> : null}
      <div className="mt-4 space-y-3">
        {faqs.map((f, i) => (
          <details key={f.question} className="faq card" open={i === 0}>
            <summary>{f.question}</summary>
            <p>{f.answer}</p>
          </details>
        ))}
      </div>
    </section>
  );
}
