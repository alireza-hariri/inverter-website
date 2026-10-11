export type SeoBlock = {
  title: string;
  description: string;
  canonical_url: string;
  og_image: string;
  no_index: boolean;
  schema_type: string;
};

export type RelatedLink = { slug: string; title?: string; name?: string; category?: string };

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
};

export type ArticleDetail = ArticleItem & {
  body: string;
  related_services: RelatedLink[];
  related_brands: RelatedLink[];
  related_articles: RelatedLink[];
};

export type HomeSite = {
  site_title: string;
  tagline: string;
  meta_description: string;
  og_image: string;
  phone: string;
  address: string;
  org_name: string;
};

export type HomeContent = {
  language: string;
  site: HomeSite;
  services: ServiceItem[];
  brands: BrandItem[];
  articles: ArticleItem[];
};

export type SitemapRecord = {
  route: string;
  slug: string;
  updated_at: string;
  no_index: boolean;
};
