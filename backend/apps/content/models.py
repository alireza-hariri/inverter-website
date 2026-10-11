from django.db import models

from apps.common.models import TimestampedModel

CATEGORY_CHOICES = (
    ("elevator", "Elevator"),
    ("industrial", "Industrial"),
    ("solar", "Solar"),
)

LANGUAGE_CHOICES = (("fa", "Persian"), ("en", "English"))


class SeoFieldsMixin(models.Model):
    seo_title_fa = models.CharField(max_length=200, blank=True)
    seo_title_en = models.CharField(max_length=200, blank=True)
    seo_description_fa = models.CharField(max_length=320, blank=True)
    seo_description_en = models.CharField(max_length=320, blank=True)
    canonical_url = models.URLField(blank=True)
    og_image = models.CharField(max_length=500, blank=True)
    no_index = models.BooleanField(default=False)
    schema_type = models.CharField(max_length=100, default="Service", blank=True)

    class Meta:
        abstract = True


class Service(TimestampedModel, SeoFieldsMixin):
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


class Article(TimestampedModel, SeoFieldsMixin):
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
    published_at = models.DateTimeField(null=True, blank=True)
    services = models.ManyToManyField(Service, related_name="articles", blank=True)
    brands = models.ManyToManyField(Brand, related_name="articles", blank=True)

    class Meta:
        ordering = ["-published_at", "-updated_at"]

    def __str__(self):
        return self.slug
