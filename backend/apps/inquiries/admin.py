from django.contrib import admin

from apps.inquiries.models import ContactInquiry


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "mobile", "service_slug", "language", "status", "created_at")
    list_filter = ("status", "language", "service_slug", "created_at")
    search_fields = ("name", "mobile", "email", "message")
    readonly_fields = ("created_at", "updated_at")
    fields = ("name", "mobile", "email", "message", "service_slug", "language",
              "status", "notes", "created_at", "updated_at")
