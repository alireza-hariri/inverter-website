from django.contrib import admin

from apps.content.models import Article, Brand, Service


def _completeness(obj, fields):
    filled = sum(1 for f in fields if getattr(obj, f, ""))
    return f"{filled}/{len(fields)}"


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("slug", "category", "title_fa", "published", "ordering", "updated_at", "completeness")
    list_filter = ("category", "published")
    search_fields = ("slug", "title_fa", "title_en")
    ordering = ("ordering",)
    actions = ("make_published", "make_unpublished")
    fieldsets = (
        ("General (عمومی)", {"fields": ("slug", "category", "published", "ordering", "image")}),
        ("Persian content (محتوای فارسی)", {"fields": ("title_fa", "summary_fa", "body_fa")}),
        ("English content", {"fields": ("title_en", "summary_en", "body_en")}),
        ("SEO فارسی — title ≤ 60, description 120–160 chars", {"fields": ("seo_title_fa", "seo_description_fa")}),
        ("SEO English", {"fields": ("seo_title_en", "seo_description_en")}),
        ("SEO advanced", {"fields": ("canonical_url", "og_image", "no_index", "schema_type")}),
    )

    def completeness(self, obj):
        return _completeness(obj, ["title_fa", "title_en", "summary_fa", "summary_en",
                                   "seo_title_fa", "seo_title_en", "seo_description_fa",
                                   "seo_description_en"])

    def make_published(self, request, queryset):
        queryset.update(published=True)
    make_published.short_description = "Publish (انتشار)"

    def make_unpublished(self, request, queryset):
        queryset.update(published=False)
    make_unpublished.short_description = "Unpublish (لغو انتشار)"


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("slug", "category", "name_fa", "published", "ordering", "updated_at", "completeness")
    list_filter = ("category", "published")
    search_fields = ("slug", "name_fa", "name_en")
    ordering = ("ordering",)
    filter_horizontal = ("services",)
    actions = ("make_published", "make_unpublished")
    fieldsets = (
        ("General (عمومی)", {"fields": ("slug", "category", "published", "ordering", "logo", "services")}),
        ("Persian content (محتوای فارسی)", {"fields": ("name_fa", "description_fa", "content_fa")}),
        ("English content", {"fields": ("name_en", "description_en", "content_en")}),
        ("SEO فارسی — title ≤ 60, description 120–160 chars", {"fields": ("seo_title_fa", "seo_description_fa")}),
        ("SEO English", {"fields": ("seo_title_en", "seo_description_en")}),
        ("SEO advanced", {"fields": ("canonical_url", "og_image", "no_index", "schema_type")}),
    )

    def completeness(self, obj):
        return _completeness(obj, ["name_fa", "name_en", "description_fa", "description_en",
                                   "seo_title_fa", "seo_title_en", "seo_description_fa",
                                   "seo_description_en"])

    def make_published(self, request, queryset):
        queryset.update(published=True)
    make_published.short_description = "Publish (انتشار)"

    def make_unpublished(self, request, queryset):
        queryset.update(published=False)
    make_unpublished.short_description = "Unpublish (لغو انتشار)"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("slug", "title_fa", "author", "published", "published_at", "updated_at", "completeness")
    list_filter = ("published",)
    search_fields = ("slug", "title_fa", "title_en")
    ordering = ("-published_at",)
    filter_horizontal = ("services", "brands")
    actions = ("make_published", "make_unpublished")
    fieldsets = (
        ("General (عمومی)", {"fields": ("slug", "author", "published", "published_at", "image", "services", "brands")}),
        ("Persian content (محتوای فارسی)", {"fields": ("title_fa", "excerpt_fa", "body_fa")}),
        ("English content", {"fields": ("title_en", "excerpt_en", "body_en")}),
        ("SEO فارسی — title ≤ 60, description 120–160 chars", {"fields": ("seo_title_fa", "seo_description_fa")}),
        ("SEO English", {"fields": ("seo_title_en", "seo_description_en")}),
        ("SEO advanced", {"fields": ("canonical_url", "og_image", "no_index", "schema_type")}),
    )

    def completeness(self, obj):
        return _completeness(obj, ["title_fa", "title_en", "excerpt_fa", "excerpt_en",
                                   "seo_title_fa", "seo_title_en", "seo_description_fa",
                                   "seo_description_en"])

    def make_published(self, request, queryset):
        queryset.update(published=True)
    make_published.short_description = "Publish (انتشار)"

    def make_unpublished(self, request, queryset):
        queryset.update(published=False)
    make_unpublished.short_description = "Unpublish (لغو انتشار)"
