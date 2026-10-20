from django.contrib import admin

from apps.content.models import Article, Brand, FaqItem, Service
from apps.seo.admin_tools import WpEditorAdmin, seo_fieldsets


class FaqInline(admin.StackedInline):
    model = FaqItem
    extra = 0
    fields = (("question_fa", "question_en"), ("answer_fa", "answer_en"), ("ordering", "published"))
    classes = ("wp-faq",)
    verbose_name = "FAQ (shown with FAQ rich-result schema)"
    verbose_name_plural = "FAQs — سوالات متداول"


class ServiceFaqInline(FaqInline):
    fk_name = "service"


class BrandFaqInline(FaqInline):
    fk_name = "brand"


class ArticleFaqInline(FaqInline):
    fk_name = "article"


@admin.register(Service)
class ServiceAdmin(WpEditorAdmin):
    preview_route = "services/{slug}"
    rich_fields = ("body_fa", "body_en")
    list_display = ("thumb", "title_fa", "title_en", "category", "status", "seo_score", "ordering", "updated_at", "view_link")
    list_display_links = ("title_fa",)
    list_editable = ("ordering",)
    list_filter = ("published", "category", "no_index")
    search_fields = ("slug", "title_fa", "title_en", "focus_keyword_fa", "focus_keyword_en")
    ordering = ("ordering",)
    prepopulated_fields = {"slug": ("title_en",)}
    inlines = (ServiceFaqInline,)
    fieldsets = (
        ("فارسی", {"fields": ("title_fa", "summary_fa", "body_fa")}),
        ("English", {"classes": ("collapse",), "fields": ("title_en", "summary_en", "body_en")}),
        *seo_fieldsets(),
        ("Publish", {"classes": ("wp-side", "wp-publish"), "fields": ("published", "slug", "category", "ordering")}),
        ("Featured image", {"classes": ("wp-side",), "fields": ("image",)}),
    )


@admin.register(Brand)
class BrandAdmin(WpEditorAdmin):
    preview_route = "brands/{slug}"
    rich_fields = ("content_fa", "content_en")
    list_display = ("thumb", "name_fa", "name_en", "category", "status", "seo_score", "ordering", "updated_at", "view_link")
    list_display_links = ("name_fa",)
    list_editable = ("ordering",)
    list_filter = ("published", "category", "no_index")
    search_fields = ("slug", "name_fa", "name_en")
    ordering = ("ordering",)
    prepopulated_fields = {"slug": ("name_en",)}
    filter_horizontal = ("services",)
    inlines = (BrandFaqInline,)
    fieldsets = (
        ("فارسی", {"fields": ("name_fa", "description_fa", "content_fa")}),
        ("English", {"classes": ("collapse",), "fields": ("name_en", "description_en", "content_en")}),
        *seo_fieldsets(),
        ("Related services", {"classes": ("collapse",), "fields": ("services",)}),
        ("Publish", {"classes": ("wp-side", "wp-publish"), "fields": ("published", "slug", "category", "ordering")}),
        ("Logo", {"classes": ("wp-side",), "fields": ("logo",)}),
    )


@admin.register(Article)
class ArticleAdmin(WpEditorAdmin):
    preview_route = "articles/{slug}"
    rich_fields = ("body_fa", "body_en")
    list_display = ("thumb", "title_fa", "author", "status", "seo_score", "published_at", "view_link")
    list_display_links = ("title_fa",)
    list_filter = ("published", "no_index", "services", "brands")
    search_fields = ("slug", "title_fa", "title_en", "body_fa", "focus_keyword_fa", "focus_keyword_en")
    date_hierarchy = "published_at"
    ordering = ("-published_at",)
    prepopulated_fields = {"slug": ("title_en",)}
    filter_horizontal = ("services", "brands")
    inlines = (ArticleFaqInline,)
    fieldsets = (
        ("فارسی", {"fields": ("title_fa", "excerpt_fa", "body_fa")}),
        ("English", {"classes": ("collapse",), "fields": ("title_en", "excerpt_en", "body_en")}),
        *seo_fieldsets(),
        ("Categories (related services & brands)", {"classes": ("collapse",), "fields": ("services", "brands")}),
        ("Publish", {"classes": ("wp-side", "wp-publish"), "fields": ("published", "published_at", "slug", "author")}),
        ("Featured image", {"classes": ("wp-side",), "fields": ("image",)}),
    )

    def get_changeform_initial_data(self, request):
        from django.utils import timezone
        return {"published_at": timezone.now(), "schema_type": "BlogPosting",
                **super().get_changeform_initial_data(request)}


@admin.register(FaqItem)
class FaqItemAdmin(admin.ModelAdmin):
    list_display = ("question_fa", "attached_to", "show_on_home", "published", "ordering")
    list_editable = ("show_on_home", "published", "ordering")
    list_filter = ("show_on_home", "published")
    search_fields = ("question_fa", "question_en", "answer_fa")
    fields = ("question_fa", "answer_fa", "question_en", "answer_en", "show_on_home",
              "service", "brand", "article", "published", "ordering")

    @admin.display(description="Attached to")
    def attached_to(self, obj):
        return obj.service or obj.brand or obj.article or ("Homepage" if obj.show_on_home else "—")
