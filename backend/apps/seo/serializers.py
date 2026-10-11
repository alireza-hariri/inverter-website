from rest_framework import serializers

from apps.seo.models import GlobalSeoSetting, Redirect, SiteSetting


class SiteSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSetting
        fields = ["language", "site_title", "tagline", "meta_description",
                  "og_image", "phone", "address", "org_name"]


class GlobalSeoSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSeoSetting
        fields = ["canonical_host", "robots_txt", "org_schema_name", "org_schema_url"]


class RedirectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redirect
        fields = ["old_path", "new_path", "status_code", "active"]


class SitemapRecordSerializer(serializers.Serializer):
    route = serializers.CharField()
    slug = serializers.CharField(allow_blank=True, required=False)
    updated_at = serializers.CharField(allow_blank=True, required=False)
    no_index = serializers.BooleanField(required=False)
