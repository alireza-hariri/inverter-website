"""The pieces that make an admin change form feel like the WordPress editor.

`WpEditorAdmin` is the base for every editable page (services, brands,
articles, page SEO). It gives the form:

- a two-column layout, with fieldsets classed `wp-side` in a right-hand
  sidebar beside the Publish box (`templates/admin/wp_change_form.html`);
- a visual/HTML editor on body fields (`static/seo/admin/editor.js`);
- a media-library picker on image URL fields (`static/seo/admin/media.js`);
- a Yoast-style SEO box on fieldsets classed `wp-seo`, with a Google preview,
  length meters and a live checklist (`static/seo/admin/seo-box.js`);
- SEO traffic-light columns on the list page, scored by `apps/seo/analysis.py`.
"""
from asgiref.local import Local
from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html, format_html_join

from apps.seo import analysis

# Per-request state for list columns. A ModelAdmin is one instance shared by
# every request, so anything stored on `self` leaks between concurrent ones.
# Not cleared after the view: the changelist is a lazy TemplateResponse whose
# columns render after the view returns. Each request overwrites its own slot.
_request_state = Local()

ASSETS = forms.Media(
    css={"all": ["seo/admin/editor.css"]},
    js=["seo/admin/media.js", "seo/admin/editor.js", "seo/admin/seo-box.js"],
)


class RichTextWidget(forms.Textarea):
    def __init__(self, lang="fa", attrs=None):
        super().__init__(attrs={"class": "wp-richtext", "data-dir": "rtl" if lang == "fa" else "ltr",
                                "rows": 18, **(attrs or {})})


class ImageUrlWidget(forms.TextInput):
    def __init__(self, attrs=None):
        super().__init__(attrs={"class": "wp-image-url vTextField", "placeholder": "https://… or choose from the media library",
                                **(attrs or {})})


class MetaDescriptionWidget(forms.Textarea):
    def __init__(self, attrs=None):
        super().__init__(attrs={"rows": 3, "class": "vLargeTextField", **(attrs or {})})


def _dot(status, title=""):
    return format_html('<span class="seo-dot seo-dot--{}" title="{}"></span>', status, title)


class WpEditorAdmin(admin.ModelAdmin):
    change_form_template = "admin/wp_change_form.html"
    # Field name patterns the widgets are matched by.
    rich_fields = ()
    image_fields = ("image", "logo", "og_image")
    # Frontend path under /<lang>/ for the Google preview; "{slug}" is filled in live.
    preview_route = ""
    save_on_top = False
    list_per_page = 30

    @property
    def media(self):
        return super().media + ASSETS

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        name = db_field.name
        if name in self.rich_fields:
            kwargs["widget"] = RichTextWidget(lang=name.rsplit("_", 1)[-1])
        elif name in self.image_fields:
            kwargs["widget"] = ImageUrlWidget()
        elif name.startswith("seo_description_"):
            kwargs["widget"] = MetaDescriptionWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        from apps.seo.models import GlobalSeoSetting, SiteSetting
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id) if object_id else None
        extra_context["seo_box"] = {
            "site_url": settings.FRONTEND_URL,
            "route": self.get_preview_route(obj),
            "model": self.model._meta.model_name,
            "separator": GlobalSeoSetting.load().title_separator,
            "site_titles": dict(SiteSetting.objects.values_list("language", "site_title")),
        }
        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_preview_route(self, obj):
        return self.preview_route

    # -- list columns ----------------------------------------------------

    def changelist_view(self, request, extra_context=None):
        # Read once per list page rather than once per row and language.
        from apps.seo.models import SiteSetting
        _request_state.site_titles = dict(SiteSetting.objects.values_list("language", "site_title"))
        return super().changelist_view(request, extra_context)

    def _site_titles(self):
        return getattr(_request_state, "site_titles", {})

    def _seo_dots(self, obj):
        dots = []
        for lang in ("fa", "en"):
            results = analysis.analyse(obj, lang, self._site_titles().get(lang, ""))
            failing = "; ".join(m for s, m in results if s != "good") or "All checks pass"
            dots.append((lang.upper(), analysis.score(results), failing))
        return format_html_join(" ", '<span class="seo-score">{}<span class="seo-dot seo-dot--{}" title="{}"></span></span>', dots)

    @admin.display(description="SEO")
    def seo_score(self, obj):
        return self._seo_dots(obj)

    @admin.display(description="")
    def thumb(self, obj):
        url = next((getattr(obj, f, "") for f in self.image_fields if getattr(obj, f, "")), "")
        if not url:
            return mark_safe('<span class="wp-thumb wp-thumb--empty"></span>')
        return format_html('<img class="wp-thumb" src="{}" alt="" loading="lazy">', url)

    @admin.display(description="Status")
    def status(self, obj):
        from django.utils import timezone
        if not obj.published:
            return mark_safe('<span class="wp-status wp-status--draft">Draft</span>')
        when = getattr(obj, "published_at", None)
        if when and when > timezone.now():
            return mark_safe('<span class="wp-status wp-status--scheduled">Scheduled</span>')
        if obj.no_index:
            return mark_safe('<span class="wp-status wp-status--noindex">Published · noindex</span>')
        return mark_safe('<span class="wp-status wp-status--live">Published</span>')

    @admin.display(description="")
    def view_link(self, obj):
        if not obj.published:
            return ""
        return format_html('<a class="wp-row-action" href="{}" target="_blank" rel="noopener">View ↗</a>',
                           obj.get_absolute_url())

    def make_published(self, request, queryset):
        updated = queryset.update(published=True)
        self.message_user(request, f"{updated} published.")
    make_published.short_description = "Publish (انتشار)"

    def make_unpublished(self, request, queryset):
        updated = queryset.update(published=False)
        self.message_user(request, f"{updated} moved to draft.")
    make_unpublished.short_description = "Move to draft (پیش‌نویس)"

    def make_noindex(self, request, queryset):
        queryset.update(no_index=True)
    make_noindex.short_description = "Set noindex"

    def make_index(self, request, queryset):
        queryset.update(no_index=False)
    make_index.short_description = "Allow indexing"

    actions = ("make_published", "make_unpublished", "make_noindex", "make_index")


def seo_fieldsets(*, with_image_alt=True):
    """The two SEO-box fieldsets plus the advanced sidebar box, for record models."""
    alt = ("image_alt_fa",) if with_image_alt else ()
    alt_en = ("image_alt_en",) if with_image_alt else ()
    return (
        ("SEO — فارسی", {"classes": ("wp-seo",), "fields": ("focus_keyword_fa", "seo_title_fa", "seo_description_fa", *alt)}),
        ("SEO — English", {"classes": ("wp-seo", "collapse"), "fields": ("focus_keyword_en", "seo_title_en", "seo_description_en", *alt_en)}),
        ("Advanced SEO", {"classes": ("wp-side", "collapse"), "fields": ("og_image", "no_index", "canonical_url", "schema_type")}),
    )
