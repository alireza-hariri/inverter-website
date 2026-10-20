from django.conf import settings
from django.db import models

from apps.common.models import TimestampedModel

CATEGORY_CHOICES = (
    ("elevator", "Elevator"),
    ("industrial", "Industrial"),
    ("solar", "Solar"),
)

SCHEMA_TYPE_CHOICES = (
    ("Service", "Service"),
    ("Product", "Product"),
    ("Brand", "Brand"),
    ("Article", "Article"),
    ("BlogPosting", "Blog post"),
    ("NewsArticle", "News article"),
    ("HowTo", "How-to"),
    ("WebPage", "Web page"),
)


class SeoFieldsMixin(models.Model):
    """The fields behind the SEO box on every editable page, Yoast-style.

    The focus keyphrase is never shown on the site: it only drives the admin's
    analysis of how well the title, description and body target that phrase.
    """
    seo_title_fa = models.CharField(
        "SEO title (fa)", max_length=200, blank=True,
        help_text="The full page title tag shown in Google. Leave blank to use “Title | Site name”.")
    seo_title_en = models.CharField(
        "SEO title (en)", max_length=200, blank=True,
        help_text="The full page title tag shown in Google. Leave blank to use “Title | Site name”.")
    seo_description_fa = models.CharField("Meta description (fa)", max_length=320, blank=True)
    seo_description_en = models.CharField("Meta description (en)", max_length=320, blank=True)
    focus_keyword_fa = models.CharField("Focus keyphrase (fa)", max_length=120, blank=True)
    focus_keyword_en = models.CharField("Focus keyphrase (en)", max_length=120, blank=True)
    image_alt_fa = models.CharField("Image alt text (fa)", max_length=200, blank=True)
    image_alt_en = models.CharField("Image alt text (en)", max_length=200, blank=True)
    canonical_url = models.URLField(
        blank=True, help_text="Only set this to point search engines at a different URL.")
    og_image = models.CharField(
        "Social share image", max_length=500, blank=True,
        help_text="Shown when the page is shared on Telegram, WhatsApp, LinkedIn… "
                  "Falls back to the main image, then the site default. 1200×630 works best.")
    no_index = models.BooleanField(
        "Hide from search engines (noindex)", default=False,
        help_text="Adds noindex (links are still followed) and drops the page from the sitemap.")
    schema_type = models.CharField(
        "Schema type", max_length=100, default="Service", blank=True,
        choices=SCHEMA_TYPE_CHOICES)

    # The frontend path segment this model lives under, e.g. "services".
    route = ""

    class Meta:
        abstract = True

    def public_path(self, lang="fa"):
        return f"/{lang}/{self.route}/{self.slug}"

    def get_absolute_url(self):
        """Absolute, so the admin's “View on site” opens the Next.js frontend."""
        return settings.FRONTEND_URL + self.public_path()


class Service(TimestampedModel, SeoFieldsMixin):
    route = "services"

    slug = models.SlugField(unique=True, max_length=120)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title_fa = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    summary_fa = models.TextField(blank=True)
    summary_en = models.TextField(blank=True)
    body_fa = models.TextField(blank=True)
    body_en = models.TextField(blank=True)
    image = models.CharField(max_length=500, blank=True)
    published = models.BooleanField(default=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordering", "-updated_at"]

    def __str__(self):
        return self.slug


class Brand(TimestampedModel, SeoFieldsMixin):
    route = "brands"

    slug = models.SlugField(unique=True, max_length=120)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    name_fa = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    description_fa = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    content_fa = models.TextField(blank=True)
    content_en = models.TextField(blank=True)
    logo = models.CharField(max_length=500, blank=True)
    published = models.BooleanField(default=True)
    ordering = models.PositiveIntegerField(default=0)
    services = models.ManyToManyField(Service, related_name="brands", blank=True)

    class Meta:
        ordering = ["ordering", "-updated_at"]

    def __str__(self):
        return self.slug


class ArticleQuerySet(models.QuerySet):
    def live(self):
        """Published, and not scheduled for later -- what WordPress calls “published”."""
        from django.utils import timezone
        return self.filter(published=True).filter(
            models.Q(published_at__isnull=True) | models.Q(published_at__lte=timezone.now()))


class Article(TimestampedModel, SeoFieldsMixin):
    route = "articles"
    objects = ArticleQuerySet.as_manager()

    slug = models.SlugField(unique=True, max_length=150)
    title_fa = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    excerpt_fa = models.TextField(blank=True)
    excerpt_en = models.TextField(blank=True)
    body_fa = models.TextField(blank=True)
    body_en = models.TextField(blank=True)
    image = models.CharField(max_length=500, blank=True)
    author = models.CharField(max_length=200, blank=True)
    published = models.BooleanField(default=True)
    published_at = models.DateTimeField(
        "Publish date", null=True, blank=True,
        help_text="A future date schedules the article: it stays hidden until then.")
    services = models.ManyToManyField(Service, related_name="articles", blank=True)
    brands = models.ManyToManyField(Brand, related_name="articles", blank=True)

    class Meta:
        ordering = ["-published_at", "-updated_at"]

    def __str__(self):
        return self.slug


class FaqItem(TimestampedModel):
    """One question and answer, rendered as an FAQ block with FAQPage schema.

    Attach it to a service, brand or article, or tick `show_on_home` for the
    homepage FAQ. FAQ rich results are among the cheapest wins in search.
    """
    question_fa = models.CharField(max_length=300)
    question_en = models.CharField(max_length=300, blank=True)
    answer_fa = models.TextField()
    answer_en = models.TextField(blank=True)
    service = models.ForeignKey(Service, null=True, blank=True, on_delete=models.CASCADE, related_name="faqs")
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.CASCADE, related_name="faqs")
    article = models.ForeignKey(Article, null=True, blank=True, on_delete=models.CASCADE, related_name="faqs")
    show_on_home = models.BooleanField("Show on homepage", default=False)
    published = models.BooleanField(default=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordering", "id"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question_fa[:80]
