import Link from "next/link";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getHome, getSeoSettings } from "@/lib/content-api";
import { buildMeta } from "@/lib/seo";
import { categoryLabel, isLang, path, t, type Lang } from "@/lib/i18n";
import Hero from "@/components/hero";
import { ArticleCard, BrandTile, ServiceCard, SectionHeading } from "@/components/cards";
import FaqList from "@/components/faq-list";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ lang: string }> }): Promise<Metadata> {
  const { lang } = await params;
  if (!isLang(lang)) return {};
  const settings = await getSeoSettings(lang).catch(() => null);
  return buildMeta(lang, settings, {
    title: settings?.site.tagline ?? "",
    description: settings?.site.meta_description,
    page: settings?.pages.home,
    image: settings?.site.og_image,
  });
}

const CATEGORIES = {
  elevator: { icon: "⇅", fa: "زیمنس، دلتا، یاسکاوا، ال‌اس، فوجی و برندهای دیگر", en: "Siemens, Delta, Yaskawa, LS, Fuji and more" },
  industrial: { icon: "⚙", fa: "دلتا، یاسکاوا، زیمنس، اشنایدر، اینوونس", en: "Delta, Yaskawa, Siemens, Schneider, Inovance" },
  solar: { icon: "☀", fa: "گراوات، سولارکس، ولترونیک، SMA و برندهای دیگر", en: "Growatt, SolarX, Voltronic, SMA and more" },
} as const;

const STEPS = {
  fa: [
    ["ثبت درخواست", "فرم را پر کنید یا تماس بگیرید؛ مدل دستگاه و علائم خرابی را بگویید."],
    ["عیب‌یابی تخصصی", "بررسی برد قدرت و کنترل و اعلام هزینه و زمان پیش از شروع کار."],
    ["تعمیر و تست زیر بار", "تعویض قطعات معیوب و تست کامل دستگاه در شرایط کاری واقعی."],
    ["تحویل با گارانتی", "تحویل دستگاه همراه با گزارش تعمیر و گارانتی خدمات."],
  ],
  en: [
    ["Send a request", "Fill in the form or call us with the model and the symptoms."],
    ["Expert diagnostics", "Power and control boards are checked; you get cost and time first."],
    ["Repair & load test", "Faulty parts are replaced and the unit is tested under real load."],
    ["Delivery with warranty", "The unit comes back with a repair report and service warranty."],
  ],
};

/**
 * Services sit on a 6-column grid so a short last row never leaves a gap:
 * the cards that would be left over widen to halves.
 */
function serviceSpan(i: number, n: number) {
  const halves = (n % 3 === 2 && i < 2) || (n % 3 === 1 && i >= n - 4);
  return halves ? "lg:col-span-3" : "lg:col-span-2";
}

export default async function HomePage({ params }: { params: Promise<{ lang: string }> }) {
  const { lang } = await params;
  if (!isLang(lang)) notFound();
  const l: Lang = lang;
  const fa = l === "fa";
  const home = await getHome(l);
  const site = home.site;
  return (
    <main>
      <Hero
        lang={l}
        title={site.hero_title || site.site_title}
        subtitle={site.hero_subtitle || site.tagline}
        phone={site.phone}
        mobile={site.mobile}
      />

      <section className="container-x relative z-10 -mt-14 md:-mt-16" aria-label={fa ? "دسته‌بندی‌ها" : "Categories"}>
        <div className="cat-strip">
          {(Object.keys(CATEGORIES) as (keyof typeof CATEGORIES)[]).map((c) => (
            <Link key={c} href={path(l, "brands") + `?category=${c}`} className="cat-card group">
              <span className="cat-card__icon" aria-hidden="true">{CATEGORIES[c].icon}</span>
              <div className="min-w-0 flex-1">
              <div className="font-extrabold group-hover:text-[#8a6a00]">{fa ? (c === "industrial" ? "درایو " : "اینورتر ") : ""}{categoryLabel(c, l)}{fa ? "" : " inverters"}</div>
                <div className="mt-1 truncate text-sm text-slate-500">{CATEGORIES[c][l]}</div>
              </div>
              <span className="link-arrow text-sm" aria-hidden="true" />
            </Link>
          ))}
        </div>
      </section>

      <div className="container-x space-y-20 pt-20 md:space-y-28">
        <section>
          <SectionHeading
            eyebrow={fa ? "خدمات" : "Services"}
            title={t("ourServices", l)}
            sub={fa ? "اینورتر آسانسور، درایو صنعتی و نیروگاه خورشیدی؛ با عیب‌یابی و تست تخصصی." : "Elevator inverters, industrial drives and solar plants—with specialist diagnostics and testing."}
            link={{ href: path(l, "services"), label: fa ? "همه خدمات" : "All services" }}
          />
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-6">
            {home.services.map((s, i) => (
              <ServiceCard key={s.slug} lang={l} s={s} className={serviceSpan(i, home.services.length)} />
            ))}
          </div>
        </section>

        <section className="process">
          <SectionHeading eyebrow={fa ? "چطور کار می‌کنیم" : "How it works"} title={t("process", l)} />
          <ol className="grid gap-5 md:grid-cols-4">
            {STEPS[l].map(([h, d], i) => (
              <li key={h} className="process__step">
                <span className="process__num">{fa ? "۱۲۳۴"[i] : i + 1}</span>
                <h3 className="mt-4 font-extrabold text-white">{h}</h3>
                <p className="mt-2 text-sm leading-7 text-white/70">{d}</p>
              </li>
            ))}
          </ol>
        </section>

        <section>
          <SectionHeading
            eyebrow={fa ? "برندها" : "Brands"}
            title={t("supportedBrands", l)}
            link={{ href: path(l, "brands"), label: fa ? "همه برندها" : "All brands" }}
          />
          <div className="brand-wall">
            {home.brands.map((b) => (<BrandTile key={b.slug} lang={l} b={b} />))}
          </div>
        </section>

        {home.faqs.length ? (
          <div className="space-y-6">
            <section className="grid items-start gap-10 md:grid-cols-[1fr_1.4fr]">
              <div className="md:sticky md:top-24">
                <div className="eyebrow">{fa ? "سوالات متداول" : "FAQ"}</div>
                <h2 className="text-2xl md:text-3xl font-black leading-tight">{fa ? "پاسخ سوالات رایج درباره تعمیر اینورتر" : "Common questions about inverter repair"}</h2>
                <p className="mt-3 leading-8 text-slate-500">{fa ? "پاسخ سوالتان را پیدا نکردید؟ با ما تماس بگیرید." : "Didn't find your answer? Get in touch."}</p>
                <Link href={path(l, "contact")} className="btn-gold mt-5 inline-block">{t("contact", l)}</Link>
              </div>
              <FaqList faqs={home.faqs} className="" />
            </section>
            <section className="card flex flex-col gap-4 p-5 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:p-6" aria-label={fa ? "تماس با کارشناس فنی" : "Contact a technical specialist"}>
              <div className="flex min-w-0 items-center gap-4">
                <div aria-hidden="true" className="grid size-16 shrink-0 place-items-center rounded-xl border border-[#f3d97b] bg-[#fff7e0] text-2xl font-black text-[#8a6a00]">
                  {fa ? "و" : "V"}
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-bold text-[#8a6a00]">{fa ? "کارشناس فنی" : "Technical specialist"}</p>
                  <h3 className="mt-1 text-lg font-black text-slate-900">{fa ? "خانم وفایی" : "Ms. Vafaei"}</h3>
                  <p className="mt-1 text-sm leading-7 text-slate-600">
                    {fa ? "برای هماهنگی و دریافت راهنمایی فنی با کارشناس ما تماس بگیرید." : "Call our specialist for technical guidance and service coordination."}
                  </p>
                </div>
              </div>
              <div className="flex flex-wrap gap-2 sm:shrink-0">
                <a href="tel:09998703705" className="btn-gold inline-flex items-center justify-center gap-2 text-sm">
                  <span aria-hidden="true">☎</span>
                  <span dir="ltr">09998703705</span>
                </a>
                <a
                  href="https://wa.me/989998703705"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#25D366] px-5 py-3 text-sm font-bold text-white transition-colors hover:bg-[#1da851]"
                >
                  <svg aria-hidden="true" viewBox="0 0 24 24" className="size-5 fill-current">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.198-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.135-.134.298-.347.446-.52.149-.174.198-.298.298-.497.1-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.064 2.875 1.213 3.074c.149.198 2.095 3.2 5.077 4.487.71.306 1.263.489 1.694.626.712.227 1.36.195 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.946L.057 24l6.304-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z" />
                  </svg>
                  {fa ? "واتساپ" : "WhatsApp"}
                </a>
              </div>
            </section>
          </div>
        ) : null}

        {home.articles.length ? (
          <section>
            <SectionHeading
              eyebrow={fa ? "مجله" : "Blog"}
              title={t("featuredArticles", l)}
              link={{ href: path(l, "articles"), label: fa ? "همه مقالات" : "All articles" }}
            />
            <div className="grid gap-5 md:grid-cols-3">
              {home.articles.slice(0, 3).map((a) => (<ArticleCard key={a.slug} lang={l} a={a} />))}
            </div>
          </section>
        ) : null}

        <section className="cta-band">
          <div>
            <h2 className="text-2xl md:text-3xl font-black">{t("contactCta", l)}</h2>
            <p className="mt-2 text-[#3d2f00]/80">{site.opening_hours_text}</p>
          </div>
          <div className="flex flex-wrap gap-3">
            {site.phone ? <a href={`tel:${site.phone.replace(/\s/g, "")}`} className="btn-dark btn-lg" dir="ltr">☎ {site.phone}</a> : null}
            {site.mobile ? <a href={`tel:${site.mobile.replace(/\s/g, "")}`} className="btn-dark btn-lg" dir="ltr">📱 {site.mobile}</a> : null}
            <Link href={path(l, "contact")} className="btn-white btn-lg">{t("requestService", l)}</Link>
          </div>
        </section>
      </div>
    </main>
  );
}
