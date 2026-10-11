from django.db import models

from apps.common.models import TimestampedModel

STATUS_CHOICES = (
    ("new", "New"),
    ("in_progress", "In progress"),
    ("resolved", "Resolved"),
)


class ContactInquiry(TimestampedModel):
    name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    message = models.TextField()
    service_slug = models.CharField(max_length=120, blank=True)
    language = models.CharField(max_length=5, default="fa")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.mobile})"
