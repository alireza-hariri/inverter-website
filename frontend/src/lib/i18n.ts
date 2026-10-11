export type Lang = "fa" | "en";

export const LANGS: Lang[] = ["fa", "en"];
export const DEFAULT_LANG: Lang = "fa";

export function isLang(v: unknown): v is Lang {
  return v === "fa" || v === "en";
}

export function dirOf(lang: Lang): "rtl" | "ltr" {
  return lang === "fa" ? "rtl" : "ltr";
}

export function otherLang(lang: Lang): Lang {
  return lang === "fa" ? "en" : "fa";
}

/** Localised UI strings. */
const STR: Record<string, { fa: string; en: string }> = {
  services: { fa: "خدمات", en: "Services" },
  brands: { fa: "برندها", en: "Brands" },
  articles: { fa: "مقالات", en: "Articles" },
  about: { fa: "درباره ما", en: "About us" },
  contact: { fa: "تماس", en: "Contact" },
  home: { fa: "خانه", en: "Home" },
  login: { fa: "ورود", en: "Sign in" },
  requestService: { fa: "درخواست تعمیر", en: "Request repair" },
  readMore: { fa: "ادامه مطلب", en: "Read more" },
  search: { fa: "جستجو", en: "Search" },
  searchPlaceholder: { fa: "جستجو در مقالات…", en: "Search articles…" },
  noResults: { fa: "نتیجه‌ای پیدا نشد.", en: "No results found." },
  backHome: { fa: "بازگشت به خانه", en: "Back to home" },
  notFound: { fa: "صفحه پیدا نشد", en: "Page not found" },
  notFoundText: {
    fa: "صفحه‌ای که دنبالش هستید وجود ندارد یا منتشر نشده است.",
    en: "The page you are looking for does not exist or is not published.",
  },
  errorTitle: { fa: "خطایی رخ داد", en: "Something went wrong" },
  errorText: {
    fa: "ارتباط با سرور برقرار نشد. لطفاً دوباره تلاش کنید.",
    en: "Could not reach the server. Please try again.",
  },
  retry: { fa: "تلاش مجدد", en: "Try again" },
  elevator: { fa: "آسانسوری", en: "Elevator" },
  industrial: { fa: "صنعتی", en: "Industrial" },
  solar: { fa: "خورشیدی (سانورتر)", en: "Solar" },
  relatedArticles: { fa: "مقالات مرتبط", en: "Related articles" },
  relatedServices: { fa: "خدمات مرتبط", en: "Related services" },
  relatedBrands: { fa: "برندهای مرتبط", en: "Related brands" },
  supportedBrands: { fa: "برندهای تحت پوشش", en: "Supported brands" },
  featuredArticles: { fa: "آخرین مقالات", en: "Latest articles" },
  ourServices: { fa: "خدمات ما", en: "Our services" },
  process: { fa: "فرایند تعمیر", en: "Repair process" },
  contactCta: { fa: "برای عیب‌یابی و تعمیر با ما در تماس باشید", en: "Contact us for troubleshooting and repair" },
  phone: { fa: "تلفن تماس", en: "Phone" },
  address: { fa: "آدرس", en: "Address" },
};

export function t(key: keyof typeof STR, lang: Lang): string {
  return (STR[key] ?? { fa: key, en: key })[lang];
}

export function categoryLabel(cat: string, lang: Lang): string {
  if (cat === "elevator") return t("elevator", lang);
  if (cat === "industrial") return t("industrial", lang);
  if (cat === "solar") return t("solar", lang);
  return cat;
}

export function path(lang: Lang, ...parts: string[]): string {
  return `/${lang}${parts.length ? "/" + parts.join("/") : ""}`;
}

export function switchPath(currentPath: string, target: Lang): string {
  const m = currentPath.match(/^\/(fa|en)(\/.*)?$/);
  if (!m) return `/${target}`;
  return `/${target}${m[2] ?? ""}`;
}

/** Accept only same-origin relative paths under /fa or /en. */
export function safeNext(next: string | null | undefined, lang: Lang): string {
  if (typeof next === "string" && /^\/(fa|en)(\/|$)/.test(next) && !next.startsWith("//")) return next;
  return path(lang);
}

/** Persian digits for fa, latin for en. */
export function num(n: number | string, lang: Lang): string {
  const s = String(n);
  if (lang !== "fa") return s;
  return s.replace(/[0-9]/g, (d) => "۰۱۲۳۴۵۶۷۸۹"[Number(d)]);
}

export function fmtDate(iso: string | null | undefined, lang: Lang): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  try {
    return new Intl.DateTimeFormat(lang === "fa" ? "fa-IR" : "en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    }).format(d);
  } catch {
    return d.toISOString().slice(0, 10);
  }
}
