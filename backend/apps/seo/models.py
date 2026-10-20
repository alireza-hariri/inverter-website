from django.core.exceptions import ValidationError
from django.db import models

from apps.common.models import TimestampedModel


class SingletonModel(TimestampedModel):
    """A settings row there is exactly one of, like a WordPress options page."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SiteSetting(TimestampedModel):
    language = models.CharField(max_length=5, unique=True, choices=(("fa", "فارسی"), ("en", "English")))
    site_title = models.CharField(
        "Site name", max_length=200,
        help_text="Appended to page titles: “Page title | Site name”.")
    tagline = models.CharField(max_length=300, blank=True)
    hero_title = models.CharField(
        "Homepage headline (H1)", max_length=200, blank=True,
        help_text="The homepage's single H1. Put the main keyphrase here, e.g. "
                  "“تعمیر تخصصی اینورتر آسانسور، صنعتی و خورشیدی”. Blank uses the site name.")
    hero_subtitle = models.TextField("Homepage intro", blank=True)
    meta_description = models.CharField(
        "Homepage meta description", max_length=320, blank=True,
        help_text="Also the fallback for any page without its own description.")
    og_image = models.CharField("Homepage social image", max_length=500, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    whatsapp = models.CharField(
        max_length=50, blank=True, help_text="International format without +, e.g. 989120000000.")
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    org_name = models.CharField("Organisation name", max_length=200, blank=True)
    opening_hours_text = models.CharField(
        "Opening hours (shown to visitors)", max_length=200, blank=True)

    class Meta:
        verbose_name = "Site identity (per language)"
        verbose_name_plural = "Site identity (per language)"

    def __str__(self):
        return f"{self.get_language_display()} — {self.site_title}"


class GlobalSeoSetting(SingletonModel):
    canonical_host = models.CharField(
        max_length=200, blank=True,
        help_text="Informational: the canonical origin, e.g. https://electrogold.ir. "
                  "The frontend's NEXT_PUBLIC_SITE_URL must match it.")
    title_separator = models.CharField(max_length=5, default="|")
    robots_txt = models.TextField(
        default="User-agent: *\nAllow: /\nDisallow: /fa/login\nDisallow: /en/login",
        blank=True,
        help_text="Served as /robots.txt. The Sitemap: line is added automatically.")
    discourage_search_engines = models.BooleanField(
        "Discourage search engines from indexing this site", default=False,
        help_text="Like WordPress's Reading setting: noindex on every page and "
                  "“Disallow: /” in robots.txt. Use it on staging only.")
    default_og_image = models.CharField(
        "Default social share image", max_length=500, blank=True,
        help_text="Used by any page that has no image of its own. 1200×630.")
    org_schema_name = models.CharField("Organisation name (schema)", max_length=200, blank=True)
    org_schema_url = models.CharField("Organisation URL (schema)", max_length=300, blank=True)
    org_logo = models.CharField("Logo URL", max_length=500, blank=True)
    business_type = models.CharField(
        "Business type (schema)", max_length=60, default="ProfessionalService",
        choices=(
            ("ProfessionalService", "Professional service"),
            ("LocalBusiness", "Local business"),
            ("ElectronicsStore", "Electronics store"),
            ("HomeAndConstructionBusiness", "Home & construction business"),
            ("Organization", "Organisation (no physical location)"),
        ),
        help_text="LocalBusiness types make the site eligible for the map/knowledge panel.")
    opening_hours = models.CharField(
        "Opening hours (schema)", max_length=200, blank=True, default="Sa-Th 08:00-18:00",
        help_text="schema.org format, e.g. “Sa-Th 08:00-18:00”. Separate several with commas.")
    price_range = models.CharField(max_length=20, blank=True, default="$$")
    latitude = models.CharField(max_length=30, blank=True)
    longitude = models.CharField(max_length=30, blank=True)
    same_as = models.TextField(
        "Social profiles", blank=True,
        help_text="One URL per line: Instagram, Telegram, LinkedIn, Aparat, YouTube…")
    google_site_verification = models.CharField(
        max_length=200, blank=True, help_text="Only the content=\"…\" value from Search Console.")
    bing_site_verification = models.CharField(max_length=200, blank=True)
    yandex_verification = models.CharField(max_length=200, blank=True)
    gtm_id = models.CharField(
        "Google Tag Manager ID", max_length=30, blank=True, help_text="GTM-XXXXXXX")
    ga4_id = models.CharField(
        "Google Analytics 4 ID", max_length=30, blank=True,
        help_text="G-XXXXXXXXXX. Leave blank if GA4 is loaded through Tag Manager.")

    class Meta:
        verbose_name = "SEO settings"
        verbose_name_plural = "SEO settings"

    def __str__(self):
        return "SEO settings"

    def same_as_list(self):
        return [line.strip() for line in self.same_as.splitlines() if line.strip()]


PAGE_CHOICES = (
    ("home", "Homepage"),
    ("services", "Services list"),
    ("brands", "Brands list"),
    ("articles", "Articles / blog list"),
    ("about", "About us"),
    ("contact", "Contact"),
)


class PageSeo(TimestampedModel):
    """SEO for the fixed pages that have no editable record of their own."""
    page = models.CharField(max_length=20, choices=PAGE_CHOICES, unique=True)
    seo_title_fa = models.CharField("SEO title (fa)", max_length=200, blank=True)
    seo_title_en = models.CharField("SEO title (en)", max_length=200, blank=True)
    seo_description_fa = models.CharField("Meta description (fa)", max_length=320, blank=True)
    seo_description_en = models.CharField("Meta description (en)", max_length=320, blank=True)
    focus_keyword_fa = models.CharField("Focus keyphrase (fa)", max_length=120, blank=True)
    focus_keyword_en = models.CharField("Focus keyphrase (en)", max_length=120, blank=True)
    intro_fa = models.TextField(
        "Intro text (fa)", blank=True,
        help_text="Shown under the page heading. Search engines read it; a few keyword-rich sentences help.")
    intro_en = models.TextField("Intro text (en)", blank=True)
    og_image = models.CharField("Social share image", max_length=500, blank=True)
    no_index = models.BooleanField("Hide from search engines (noindex)", default=False)

    class Meta:
        ordering = ["id"]
        verbose_name = "Page SEO"
        verbose_name_plural = "Pages SEO"

    def __str__(self):
        return self.get_page_display()

    def public_path(self, lang="fa"):
        return f"/{lang}" if self.page == "home" else f"/{lang}/{self.page}"

    def get_absolute_url(self):
        from django.conf import settings
        return settings.FRONTEND_URL + self.public_path()


REDIRECT_CODES = (
    (301, "301 Moved permanently"),
    (302, "302 Found (temporary)"),
    (307, "307 Temporary redirect"),
    (308, "308 Permanent redirect"),
    (410, "410 Gone (content deleted)"),
)


def normalise_path(value):
    """`/Fa/Old-Page/` and `/fa/old-page` are one URL to a visitor; store one form."""
    value = (value or "").strip()
    if value.startswith(("http://", "https://")):
        return value
    if not value.startswith("/"):
        value = "/" + value
    return value.rstrip("/") or "/"


class Redirect(TimestampedModel):
    old_path = models.CharField(
        "Source URL", max_length=500, unique=True,
        help_text="Path on this site, e.g. /fa/old-article. Query strings are ignored.")
    new_path = models.CharField(
        "Target URL", max_length=500, blank=True,
        help_text="A path on this site (/fa/services) or a full URL. Leave blank for 410.")
    status_code = models.PositiveSmallIntegerField("Type", default=301, choices=REDIRECT_CODES)
    active = models.BooleanField(default=True)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["old_path"]

    def __str__(self):
        return f"{self.old_path} → {self.new_path or self.status_code}"

    def clean(self):
        self.old_path = normalise_path(self.old_path)
        if self.old_path.startswith(("http://", "https://")):
            raise ValidationError({"old_path": "Use a path on this site, starting with /."})
        if self.status_code != 410:
            if not self.new_path:
                raise ValidationError({"new_path": "A redirect needs a target."})
            self.new_path = normalise_path(self.new_path)
            if self.new_path == self.old_path:
                raise ValidationError({"new_path": "The target is the same as the source."})
            loop = Redirect.objects.filter(old_path=self.new_path, new_path=self.old_path, active=True)
            if self.pk:
                loop = loop.exclude(pk=self.pk)
            if loop.exists():
                raise ValidationError({"new_path": "That target already redirects back here — a loop."})


class NotFoundLog(TimestampedModel):
    """404s the frontend served, so broken links can be redirected (Redirection-plugin style)."""
    path = models.CharField(max_length=500, unique=True)
    hits = models.PositiveIntegerField(default=1)
    last_referrer = models.CharField(max_length=500, blank=True)
    last_seen = models.DateTimeField(auto_now=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-hits"]
        verbose_name = "404 error"
        verbose_name_plural = "404 monitor"

    def __str__(self):
        return self.path


class MediaFile(TimestampedModel):
    """An uploaded image, with alt text, usable anywhere a URL is asked for."""
    file = models.ImageField(upload_to="uploads/%Y/%m/")
    title = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Media file"
        verbose_name_plural = "Media library"

    def __str__(self):
        return self.title or self.file.name.rsplit("/", 1)[-1]
