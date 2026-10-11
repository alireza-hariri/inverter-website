from django.contrib import admin

from apps.seo.models import GlobalSeoSetting, Redirect, SiteSetting


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("language", "site_title", "phone", "updated_at")
    list_filter = ("language",)
    search_fields = ("site_title", "org_name")
    fieldsets = (
        ("Language & branding (زبان و برند)", {"fields": ("language", "site_title", "tagline", "org_name")}),
        ("SEO defaults (پیش‌فرض سئو — description 120–160 chars)", {"fields": ("meta_description", "og_image")}),
        ("Contact (تماس)", {"fields": ("phone", "address")}),
    )


@admin.register(GlobalSeoSetting)
class GlobalSeoSettingAdmin(admin.ModelAdmin):
    list_display = ("org_schema_name", "canonical_host", "updated_at")
    fieldsets = (
        ("Canonical & robots", {"fields": ("canonical_host", "robots_txt")}),
        ("Organization schema", {"fields": ("org_schema_name", "org_schema_url")}),
    )


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ("old_path", "new_path", "status_code", "active", "updated_at")
    list_filter = ("status_code", "active")
    search_fields = ("old_path", "new_path")
