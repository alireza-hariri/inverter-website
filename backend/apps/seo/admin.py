from asgiref.local import Local
from django.contrib import admin, messages
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.views.decorators.http import require_POST

from apps.seo.admin_tools import ImageUrlWidget, MetaDescriptionWidget, WpEditorAdmin
from apps.seo.models import GlobalSeoSetting, MediaFile, NotFoundLog, PageSeo, Redirect, SiteSetting


# The request being served, for display methods that need it to build absolute
# URLs. Kept out of `self`: a ModelAdmin is one instance shared by all requests.
# Not cleared after the view: admin views return a lazy TemplateResponse whose
# columns render after the view returns. Each request overwrites its own slot.
_request_state = Local()


class SingletonAdmin(admin.ModelAdmin):
    """One row, edited in place: the list page goes straight to the form, like WP Settings."""

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = self.model.load()
        return HttpResponseRedirect(reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.pk]))

    def response_change(self, request, obj):
        self.message_user(request, "Settings saved.", messages.SUCCESS)
        return HttpResponseRedirect(request.path)


@admin.register(GlobalSeoSetting)
class GlobalSeoSettingAdmin(SingletonAdmin):
    fieldsets = (
        ("General", {"fields": ("title_separator", "default_og_image", "canonical_host")}),
        ("Search engine visibility", {"fields": ("discourage_search_engines", "robots_txt")}),
        ("Webmaster tools verification", {
            "description": "Paste only the content value of each verification meta tag.",
            "fields": ("google_site_verification", "bing_site_verification", "yandex_verification")}),
        ("Analytics", {"fields": ("gtm_id", "ga4_id")}),
        ("Knowledge graph & local business (schema.org)", {
            "description": "Feeds the Organization/LocalBusiness structured data on every page.",
            "fields": ("org_schema_name", "org_schema_url", "org_logo", "business_type",
                       "opening_hours", "price_range", ("latitude", "longitude"))}),
        ("Social profiles", {"fields": ("same_as",)}),
    )

    @property
    def media(self):
        from apps.seo.admin_tools import ASSETS
        return super().media + ASSETS

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ("default_og_image", "org_logo"):
            kwargs["widget"] = ImageUrlWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("language", "site_title", "hero_title", "phone", "updated_at")
    fieldsets = (
        ("Identity", {"fields": ("language", "site_title", "tagline", "org_name")}),
        ("Homepage", {"fields": ("hero_title", "hero_subtitle", "meta_description", "og_image")}),
        ("Contact (also used in LocalBusiness schema)", {
            "fields": ("phone", "whatsapp", "email", "city", "address", "opening_hours_text")}),
    )

    @property
    def media(self):
        from apps.seo.admin_tools import ASSETS
        return super().media + ASSETS

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "og_image":
            kwargs["widget"] = ImageUrlWidget()
        elif db_field.name == "meta_description":
            kwargs["widget"] = MetaDescriptionWidget(attrs={"data-counter": "160"})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(PageSeo)
class PageSeoAdmin(WpEditorAdmin):
    list_display = ("page", "seo_title_fa", "title_length", "description_length", "noindex_flag", "updated_at", "view_link")
    actions = ()
    fieldsets = (
        ("SEO — فارسی", {"classes": ("wp-seo",), "fields": ("focus_keyword_fa", "seo_title_fa", "seo_description_fa", "intro_fa")}),
        ("SEO — English", {"classes": ("wp-seo", "collapse"), "fields": ("focus_keyword_en", "seo_title_en", "seo_description_en", "intro_en")}),
        ("Page", {"classes": ("wp-side", "wp-publish"), "fields": ("page", "no_index")}),
        ("Social share image", {"classes": ("wp-side",), "fields": ("og_image",)}),
    )

    def get_readonly_fields(self, request, obj=None):
        return ("page",) if obj else ()

    def has_delete_permission(self, request, obj=None):
        return False

    def get_preview_route(self, obj):
        return "" if not obj or obj.page == "home" else obj.page

    @admin.display(description="Title (fa)")
    def title_length(self, obj):
        return _length_badge(len(obj.seo_title_fa), 30, 60)

    @admin.display(description="Description (fa)")
    def description_length(self, obj):
        return _length_badge(len(obj.seo_description_fa), 120, 160)

    @admin.display(description="Indexing", boolean=False)
    def noindex_flag(self, obj):
        return mark_safe('<span class="wp-status wp-status--noindex">noindex</span>') if obj.no_index else "index"

    @admin.display(description="")
    def view_link(self, obj):
        return format_html('<a class="wp-row-action" href="{}" target="_blank" rel="noopener">View ↗</a>', obj.get_absolute_url())


def _length_badge(n, lo, hi):
    status = "good" if lo <= n <= hi else ("ok" if n else "bad")
    return format_html('<span class="seo-score"><span class="seo-dot seo-dot--{}"></span>{} chars</span>', status, n)


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ("old_path", "arrow", "new_path", "status_code", "active", "note", "updated_at")
    list_display_links = ("old_path",)
    list_editable = ("active",)
    list_filter = ("status_code", "active")
    search_fields = ("old_path", "new_path", "note")
    fields = ("old_path", "new_path", "status_code", "active", "note")

    @admin.display(description="")
    def arrow(self, obj):
        return "→"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        resolved = NotFoundLog.objects.filter(path=obj.old_path, resolved=False).update(resolved=True)
        if resolved:
            self.message_user(request, "The matching 404 in the 404 monitor was marked resolved.")


@admin.register(NotFoundLog)
class NotFoundLogAdmin(admin.ModelAdmin):
    list_display = ("path", "hits", "last_seen", "referrer", "resolved", "fix")
    list_filter = ("resolved",)
    search_fields = ("path", "last_referrer")
    readonly_fields = ("path", "hits", "last_referrer", "last_seen", "created_at")
    fields = ("path", "hits", "last_referrer", "last_seen", "created_at", "resolved")
    actions = ("mark_resolved",)

    def has_add_permission(self, request):
        return False

    @admin.display(description="Referrer")
    def referrer(self, obj):
        return obj.last_referrer[:80]

    @admin.display(description="")
    def fix(self, obj):
        if obj.resolved:
            return ""
        url = reverse("admin:seo_redirect_add") + f"?old_path={obj.path}&status_code=301"
        return format_html('<a class="button" href="{}">Add redirect</a>', url)

    @admin.action(description="Mark resolved")
    def mark_resolved(self, request, queryset):
        queryset.update(resolved=True)


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ("preview", "__str__", "alt_text", "url_field", "created_at")
    search_fields = ("title", "alt_text", "file")
    fields = ("file", "title", "alt_text", "preview_large", "url_field")
    readonly_fields = ("preview_large", "url_field")

    @admin.display(description="")
    def preview(self, obj):
        return format_html('<img class="wp-thumb" src="{}" alt="">', obj.file.url) if obj.file else ""

    @admin.display(description="Preview")
    def preview_large(self, obj):
        return format_html('<img style="max-width:320px;border-radius:4px" src="{}" alt="">', obj.file.url) if obj.file else "—"

    @admin.display(description="File URL")
    def url_field(self, obj):
        if not obj.file:
            return "—"
        url = self._absolute(obj)
        return format_html('<input class="vTextField wp-copy" readonly value="{}" onclick="this.select()">', url)

    def _absolute(self, obj):
        request = getattr(_request_state, "request", None)
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url

    def changeform_view(self, request, *args, **kwargs):
        _request_state.request = request
        return super().changeform_view(request, *args, **kwargs)

    def changelist_view(self, request, *args, **kwargs):
        _request_state.request = request
        return super().changelist_view(request, *args, **kwargs)

    def get_urls(self):
        extra = [
            path("browse/", self.admin_site.admin_view(self.browse), name="seo_mediafile_browse"),
            path("upload/", self.admin_site.admin_view(require_POST(self.upload)), name="seo_mediafile_upload"),
        ]
        return extra + super().get_urls()

    def _json(self, request, obj):
        return {"id": obj.pk, "url": request.build_absolute_uri(obj.file.url),
                "title": str(obj), "alt": obj.alt_text}

    def browse(self, request):
        """The media-library modal's grid: the latest uploads, optionally searched."""
        qs = MediaFile.objects.all()
        if q := request.GET.get("q"):
            qs = qs.filter(title__icontains=q) | qs.filter(alt_text__icontains=q)
        return JsonResponse({"results": [self._json(request, m) for m in qs[:60]]})

    def upload(self, request):
        if not self.has_add_permission(request):
            return JsonResponse({"error": "You may not upload media."}, status=403)
        upload = request.FILES.get("file")
        if not upload:
            return JsonResponse({"error": "No file sent."}, status=400)
        from django import forms

        class UploadForm(forms.ModelForm):
            class Meta:
                model = MediaFile
                fields = ("file", "title", "alt_text")

        form = UploadForm(data={"title": request.POST.get("title") or upload.name.rsplit(".", 1)[0],
                                "alt_text": request.POST.get("alt", "")},
                          files={"file": upload})
        if not form.is_valid():
            return JsonResponse({"error": "; ".join(e for errs in form.errors.values() for e in errs)}, status=400)
        return JsonResponse(self._json(request, form.save()), status=201)
