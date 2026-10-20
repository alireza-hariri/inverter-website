import Link from "next/link";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getHome, getSeoSettings } from "@/lib/content-api";
import { buildMeta } from "@/lib/seo";
import { categoryLabel, isLang, path, t, type Lang } from "@/lib/i18n";
import Hero from "@/components/hero";
import { ArticleCard, BrandCard, ServiceCard, SectionHeading } from "@/components/cards";
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
  elevator: { icon: "⇅", fa: "یاسکاوا، مونارک، اچ‌پی‌مونت، زیلابگ", en: "Yaskawa, Monarch, HPMont, Zilabeg" },
  industrial: { icon: "⚙", fa: "دلتا، یاسکاوا، اینوونس", en: "Delta, Yaskawa, Inovance" },
  solar: { icon: "☀", fa: "سانورترهای گرووات", en: "Growatt solar inverters" },
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
        image={home.services[0]?.image}
      />

      <section className="container-x -mt-10 relative z-10" aria-label={fa ? "دسته‌بندی‌ها" : "Categories"}>
        <div className="grid gap-4 md:grid-cols-3">
          {(Object.keys(CATEGORIES) as (keyof typeof CATEGORIES)[]).map((c) => (
            <Link key={c} href={path(l, "brands") + `?category=${c}`} className="card card-hover cat-card">
              <span className="cat-card__icon" aria-hidden="true">{CATEGORIES[c].icon}</span>
              <div>
                <div className="font-extrabold">{fa ? "اینورتر " : ""}{categoryLabel(c, l)}{fa ? "" : " inverters"}</div>
                <div className="mt-1 text-sm text-slate-500">{CATEGORIES[c][l]}</div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      <div className="container-x space-y-24 py-20">
        <section>
          <SectionHeading
            eyebrow={fa ? "خدمات" : "Services"}
            title={t("ourServices", l)}
            sub={fa ? "از اینورتر آسانسور تا سانورتر خورشیدی؛ هر دستگاه پس از تعمیر زیر بار تست می‌شود." : "From elevator drives to solar inverters — every unit is load-tested after repair."}
            link={{ href: path(l, "services"), label: fa ? "همه خدمات" : "All services" }}
          />
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {home.services.map((s) => (<ServiceCard key={s.slug} lang={l} s={s} />))}
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
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {home.brands.map((b) => (<BrandCard key={b.slug} lang={l} b={b} />))}
          </div>
        </section>

        {home.faqs.length ? (
          <section className="grid gap-10 md:grid-cols-[1fr_1.4fr]">
            <div>
              <div className="eyebrow">{fa ? "سوالات متداول" : "FAQ"}</div>
              <h2 className="text-2xl md:text-3xl font-black leading-tight">{fa ? "پاسخ سوالات رایج درباره تعمیر اینورتر" : "Common questions about inverter repair"}</h2>
              <p className="mt-3 leading-8 text-slate-500">{fa ? "پاسخ سوالتان را پیدا نکردید؟ با ما تماس بگیرید." : "Didn't find your answer? Get in touch."}</p>
              <Link href={path(l, "contact")} className="btn-gold mt-5 inline-block">{t("contact", l)}</Link>
            </div>
            <div className="-mt-10"><FaqList faqs={home.faqs} /></div>
          </section>
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
            <Link href={path(l, "contact")} className="btn-white btn-lg">{t("requestService", l)}</Link>
          </div>
        </section>
      </div>
    </main>
  );
}
