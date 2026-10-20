from rest_framework import serializers

from apps.common.i18n import pick
from apps.seo.models import GlobalSeoSetting, PageSeo, Redirect, SiteSetting

DEFAULT_SITE_TITLE = {"fa": "الکتروگلد", "en": "ElectroGold"}
SITE_FIELDS = ["site_title", "tagline", "hero_title", "hero_subtitle", "meta_description", "og_image",
               "phone", "whatsapp", "email", "address", "city", "org_name", "opening_hours_text"]


def site_block(lang):
    """The per-language site identity, with defaults when none was saved yet."""
    setting = SiteSetting.objects.filter(language=lang).first()
    if setting is None:
        return {**{f: "" for f in SITE_FIELDS}, "site_title": DEFAULT_SITE_TITLE[lang]}
    return {f: getattr(setting, f) or "" for f in SITE_FIELDS}


class GlobalSeoSettingSerializer(serializers.ModelSerializer):
    same_as = serializers.SerializerMethodField()
    verification = serializers.SerializerMethodField()

    class Meta:
        model = GlobalSeoSetting
        fields = ["canonical_host", "title_separator", "discourage_search_engines", "default_og_image",
                  "org_schema_name", "org_schema_url", "org_logo", "business_type", "opening_hours",
                  "price_range", "latitude", "longitude", "same_as", "verification", "gtm_id", "ga4_id"]

    def get_same_as(self, obj):
        return obj.same_as_list()

    def get_verification(self, obj):
        return {"google": obj.google_site_verification, "bing": obj.bing_site_verification,
                "yandex": obj.yandex_verification}


def page_block(page, lang):
    return {
        "page": page.page,
        "title": pick(page, "seo_title", lang),
        "description": pick(page, "seo_description", lang),
        "intro": pick(page, "intro", lang),
        "og_image": page.og_image,
        "no_index": page.no_index,
    }


class RedirectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redirect
        fields = ["old_path", "new_path", "status_code"]


class NotFoundReportSerializer(serializers.Serializer):
    path = serializers.CharField(max_length=500)
    referrer = serializers.CharField(max_length=500, allow_blank=True, required=False)
