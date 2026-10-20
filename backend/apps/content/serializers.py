from rest_framework import serializers

from apps.common.i18n import DEFAULT_LANGUAGE, LANGUAGES, pick
from apps.content import richtext
from apps.content.models import Article, Brand, Service


def faq_list(qs, lang):
    """Published FAQs in `lang`; an English page skips questions never translated."""
    out = []
    for f in qs.filter(published=True):
        q, a = pick(f, "question", lang), pick(f, "answer", lang)
        if q and a:
            out.append({"question": q, "answer": a})
    return out


def rich(obj, base, lang):
    """`(html, toc)` for a body field -- see apps/content/richtext.py.

    Memoised on the instance: the `*_html` and `toc` fields both need it.
    """
    cache = obj.__dict__.setdefault("_rich_cache", {})
    if (base, lang) not in cache:
        cache[(base, lang)] = richtext.render(pick(obj, base, lang))
    return cache[(base, lang)]


def seo_block(obj, lang):
    return {
        "title": pick(obj, "seo_title", lang),
        "description": pick(obj, "seo_description", lang),
        "canonical_url": getattr(obj, "canonical_url", ""),
        "og_image": getattr(obj, "og_image", ""),
        "no_index": getattr(obj, "no_index", False),
        "schema_type": getattr(obj, "schema_type", ""),
        "image_alt": pick(obj, "image_alt", lang),
    }


# The short link shapes a detail page shows for its related records.

def service_links(qs, lang):
    return [{"slug": s.slug, "category": s.category, "title": pick(s, "title", lang)}
            for s in qs.filter(published=True)]


def brand_links(qs, lang):
    return [{"slug": b.slug, "category": b.category, "name": pick(b, "name", lang)}
            for b in qs.filter(published=True)]


def article_links(qs, lang):
    return [{"slug": a.slug, "title": pick(a, "title", lang), "image": a.image} for a in qs]


class LocalizedSerializer(serializers.ModelSerializer):
    """Reads one language's side of the `_fa`/`_en` columns, from context["language"]."""

    def _lang(self):
        lang = self.context.get("language", DEFAULT_LANGUAGE)
        return lang if lang in LANGUAGES else DEFAULT_LANGUAGE

    def get_seo(self, obj):
        return seo_block(obj, self._lang())


class RichBodyMixin:
    """The rendered body, its table of contents and FAQs, for a detail serializer.

    `rich_field` names the body column; the subclass declares the fields.
    """
    rich_field = "body"

    def get_raw_body(self, obj):
        return pick(obj, self.rich_field, self._lang())

    def get_body_html(self, obj):
        return rich(obj, self.rich_field, self._lang())[0]

    def get_toc(self, obj):
        return rich(obj, self.rich_field, self._lang())[1]

    def get_faqs(self, obj):
        return faq_list(obj.faqs.all(), self._lang())


class ServiceListSerializer(LocalizedSerializer):
    title = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    seo = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ["slug", "category", "title", "summary", "image", "seo",
                  "published", "ordering", "updated_at"]

    def get_title(self, obj):
        return pick(obj, "title", self._lang())

    def get_summary(self, obj):
        return pick(obj, "summary", self._lang())


class ServiceDetailSerializer(RichBodyMixin, ServiceListSerializer):
    body = serializers.SerializerMethodField(method_name="get_raw_body")
    body_html = serializers.SerializerMethodField()
    toc = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()
    related_brands = serializers.SerializerMethodField()
    related_articles = serializers.SerializerMethodField()

    class Meta(ServiceListSerializer.Meta):
        fields = ServiceListSerializer.Meta.fields + ["body", "body_html", "toc", "faqs",
                                                      "related_brands", "related_articles"]

    def get_related_brands(self, obj):
        return brand_links(obj.brands.all(), self._lang())

    def get_related_articles(self, obj):
        return article_links(obj.articles.live()[:6], self._lang())


class BrandListSerializer(LocalizedSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    seo = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ["slug", "category", "name", "description", "logo", "seo",
                  "published", "ordering", "updated_at"]

    def get_name(self, obj):
        return pick(obj, "name", self._lang())

    def get_description(self, obj):
        return pick(obj, "description", self._lang())


class BrandDetailSerializer(RichBodyMixin, BrandListSerializer):
    rich_field = "content"

    content = serializers.SerializerMethodField(method_name="get_raw_body")
    content_html = serializers.SerializerMethodField(method_name="get_body_html")
    toc = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()
    related_services = serializers.SerializerMethodField()
    related_articles = serializers.SerializerMethodField()

    class Meta(BrandListSerializer.Meta):
        fields = BrandListSerializer.Meta.fields + ["content", "content_html", "toc", "faqs",
                                                    "related_services", "related_articles"]

    def get_related_services(self, obj):
        return service_links(obj.services.all(), self._lang())

    def get_related_articles(self, obj):
        return article_links(obj.articles.live()[:6], self._lang())


class ArticleListSerializer(LocalizedSerializer):
    title = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    seo = serializers.SerializerMethodField()
    reading_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ["slug", "title", "excerpt", "image", "author", "seo",
                  "published", "published_at", "updated_at", "reading_minutes"]

    def get_title(self, obj):
        return pick(obj, "title", self._lang())

    def get_excerpt(self, obj):
        return pick(obj, "excerpt", self._lang())

    def get_reading_minutes(self, obj):
        return richtext.reading_minutes(pick(obj, "body", self._lang()))


class ArticleDetailSerializer(RichBodyMixin, ArticleListSerializer):
    body = serializers.SerializerMethodField(method_name="get_raw_body")
    body_html = serializers.SerializerMethodField()
    toc = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()
    related_services = serializers.SerializerMethodField()
    related_brands = serializers.SerializerMethodField()
    related_articles = serializers.SerializerMethodField()

    class Meta(ArticleListSerializer.Meta):
        fields = ArticleListSerializer.Meta.fields + ["body", "body_html", "toc", "faqs", "related_services",
                                                      "related_brands", "related_articles"]

    def get_related_services(self, obj):
        return service_links(obj.services.all(), self._lang())

    def get_related_brands(self, obj):
        return brand_links(obj.brands.all(), self._lang())

    def get_related_articles(self, obj):
        qs = Article.objects.live().exclude(pk=obj.pk).order_by("-published_at")[:4]
        return article_links(qs, self._lang())
