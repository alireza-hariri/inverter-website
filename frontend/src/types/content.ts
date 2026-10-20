export type SeoBlock = {
  title: string;
  description: string;
  canonical_url: string;
  og_image: string;
  no_index: boolean;
  schema_type: string;
  image_alt: string;
};

export type Faq = { question: string; answer: string };
export type TocEntry = { id: string; text: string; level: number };

export type RelatedLink = { slug: string; title?: string; name?: string; category?: string; image?: string };

export type ServiceItem = {
  slug: string;
  category: string;
  title: string;
  summary: string;
  image: string;
  seo: SeoBlock;
  published: boolean;
  ordering: number;
  updated_at: string;
};

export type ServiceDetail = ServiceItem & {
  body: string;
  body_html: string;
  toc: TocEntry[];
  faqs: Faq[];
  related_brands: RelatedLink[];
  related_articles: RelatedLink[];
};

export type BrandItem = {
  slug: string;
  category: string;
  name: string;
  description: string;
  logo: string;
  seo: SeoBlock;
  published: boolean;
  ordering: number;
  updated_at: string;
};

export type BrandDetail = BrandItem & {
  content: string;
  content_html: string;
  toc: TocEntry[];
  faqs: Faq[];
  related_services: RelatedLink[];
  related_articles: RelatedLink[];
};

export type ArticleItem = {
  slug: string;
  title: string;
  excerpt: string;
  image: string;
  author: string;
  seo: SeoBlock;
  published: boolean;
  published_at: string | null;
  updated_at: string;
  reading_minutes: number;
};

export type ArticleDetail = ArticleItem & {
  body: string;
  body_html: string;
  toc: TocEntry[];
  faqs: Faq[];
  related_services: RelatedLink[];
  related_brands: RelatedLink[];
  related_articles: RelatedLink[];
};

export type HomeSite = {
  site_title: string;
  tagline: string;
  hero_title: string;
  hero_subtitle: string;
  meta_description: string;
  og_image: string;
  phone: string;
  whatsapp: string;
  email: string;
  address: string;
  city: string;
  org_name: string;
  opening_hours_text: string;
};

export type HomeContent = {
  language: string;
  site: HomeSite;
  services: ServiceItem[];
  brands: BrandItem[];
  articles: ArticleItem[];
  faqs: Faq[];
};

export type SitemapRecord = {
  route: string;
  slug: string;
  updated_at: string;
  no_index: boolean;
};

/** SEO for a fixed page (home, services list…), edited under "Pages SEO" in the admin. */
export type PageSeo = {
  page: string;
  title: string;
  description: string;
  intro: string;
  og_image: string;
  no_index: boolean;
};

export type GlobalSeo = {
  canonical_host: string;
  title_separator: string;
  discourage_search_engines: boolean;
  default_og_image: string;
  org_schema_name: string;
  org_schema_url: string;
  org_logo: string;
  business_type: string;
  opening_hours: string;
  price_range: string;
  latitude: string;
  longitude: string;
  same_as: string[];
  verification: { google: string; bing: string; yandex: string };
  gtm_id: string;
  ga4_id: string;
};

export type SeoSettings = {
  site: HomeSite;
  global: GlobalSeo;
  pages: Record<string, PageSeo>;
};

export type RedirectRule = { old_path: string; new_path: string; status_code: number };
