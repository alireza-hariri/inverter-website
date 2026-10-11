from rest_framework import serializers

from apps.content.models import Article, Brand, Service

VALID_LANGUAGES = ("fa", "en")


def pick(obj, base, lang):
    return getattr(obj, f"{base}_{lang}", "") or ""


def seo_block(obj, lang):
    return {
        "title": pick(obj, "seo_title", lang),
        "description": pick(obj, "seo_description", lang),
        "canonical_url": getattr(obj, "canonical_url", ""),
        "og_image": getattr(obj, "og_image", ""),
        "no_index": getattr(obj, "no_index", False),
        "schema_type": getattr(obj, "schema_type", ""),
    }


class ServiceListSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    seo = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ["slug", "category", "title", "summary", "image", "seo",
                  "published", "ordering", "updated_at"]

    def _lang(self):
        lang = self.context.get("language", "fa")
        return lang if lang in VALID_LANGUAGES else "fa"

    def get_title(self, obj):
        return pick(obj, "title", self._lang())

    def get_summary(self, obj):
        return pick(obj, "summary", self._lang())

    def get_seo(self, obj):
        return seo_block(obj, self._lang())


class ServiceDetailSerializer(ServiceListSerializer):
    body = serializers.SerializerMethodField()
    related_brands = serializers.SerializerMethodField()
    related_articles = serializers.SerializerMethodField()

    class Meta(ServiceListSerializer.Meta):
        fields = ServiceListSerializer.Meta.fields + ["body", "related_brands", "related_articles"]

    def get_body(self, obj):
        return pick(obj, "body", self._lang())

    def get_related_brands(self, obj):
        lang = self._lang()
        return [{"slug": b.slug, "category": b.category,
                 "name": pick(b, "name", lang)} for b in obj.brands.filter(published=True)]

    def get_related_articles(self, obj):
        lang = self._lang()
        return [{"slug": a.slug, "title": pick(a, "title", lang)}
                for a in obj.articles.filter(published=True)[:6]]


class BrandListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    seo = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ["slug", "category", "name", "description", "logo", "seo",
                  "published", "ordering", "updated_at"]

    def _lang(self):
        lang = self.context.get("language", "fa")
        return lang if lang in VALID_LANGUAGES else "fa"

    def get_name(self, obj):
        return pick(obj, "name", self._lang())

    def get_description(self, obj):
        return pick(obj, "description", self._lang())

    def get_seo(self, obj):
        return seo_block(obj, self._lang())


class BrandDetailSerializer(BrandListSerializer):
    content = serializers.SerializerMethodField()
    related_services = serializers.SerializerMethodField()
    related_articles = serializers.SerializerMethodField()

    class Meta(BrandListSerializer.Meta):
        fields = BrandListSerializer.Meta.fields + ["content", "related_services", "related_articles"]

    def get_content(self, obj):
        return pick(obj, "content", self._lang())

    def get_related_services(self, obj):
        lang = self._lang()
        return [{"slug": s.slug, "category": s.category,
                 "title": pick(s, "title", lang)} for s in obj.services.filter(published=True)]

    def get_related_articles(self, obj):
        lang = self._lang()
        return [{"slug": a.slug, "title": pick(a, "title", lang)}
                for a in obj.articles.filter(published=True)[:6]]


class ArticleListSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    seo = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ["slug", "title", "excerpt", "image", "author", "seo",
                  "published", "published_at", "updated_at"]

    def _lang(self):
        lang = self.context.get("language", "fa")
        return lang if lang in VALID_LANGUAGES else "fa"

    def get_title(self, obj):
        return pick(obj, "title", self._lang())

    def get_excerpt(self, obj):
        return pick(obj, "excerpt", self._lang())

    def get_seo(self, obj):
        return seo_block(obj, self._lang())


class ArticleDetailSerializer(ArticleListSerializer):
    body = serializers.SerializerMethodField()
    related_services = serializers.SerializerMethodField()
    related_brands = serializers.SerializerMethodField()
    related_articles = serializers.SerializerMethodField()

    class Meta(ArticleListSerializer.Meta):
        fields = ArticleListSerializer.Meta.fields + ["body", "related_services",
                                                      "related_brands", "related_articles"]

    def get_body(self, obj):
        return pick(obj, "body", self._lang())

    def get_related_services(self, obj):
        lang = self._lang()
        return [{"slug": s.slug, "category": s.category,
                 "title": pick(s, "title", lang)} for s in obj.services.filter(published=True)]

    def get_related_brands(self, obj):
        lang = self._lang()
        return [{"slug": b.slug, "category": b.category,
                 "name": pick(b, "name", lang)} for b in obj.brands.filter(published=True)]

    def get_related_articles(self, obj):
        lang = self._lang()
        qs = Article.objects.filter(published=True).exclude(pk=obj.pk).order_by("-published_at")[:4]
        return [{"slug": a.slug, "title": pick(a, "title", lang)} for a in qs]
