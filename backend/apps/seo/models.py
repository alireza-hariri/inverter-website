from django.db import models

from apps.common.models import TimestampedModel


class SiteSetting(TimestampedModel):
    language = models.CharField(max_length=5, unique=True)
    site_title = models.CharField(max_length=200)
    tagline = models.CharField(max_length=300, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)
    og_image = models.CharField(max_length=500, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    org_name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"SiteSetting({self.language})"


class GlobalSeoSetting(TimestampedModel):
    canonical_host = models.CharField(max_length=200, blank=True)
    robots_txt = models.TextField(
        default="User-agent: *\nAllow: /", blank=True
    )
    org_schema_name = models.CharField(max_length=200, blank=True)
    org_schema_url = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return "GlobalSeoSetting"


class Redirect(TimestampedModel):
    old_path = models.CharField(max_length=500, unique=True)
    new_path = models.CharField(max_length=500)
    status_code = models.PositiveSmallIntegerField(default=301)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.old_path} -> {self.new_path}"
