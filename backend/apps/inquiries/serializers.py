from rest_framework import serializers

from apps.inquiries.models import ContactInquiry


class ContactInquirySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=200)
    mobile = serializers.CharField(max_length=30)
    service = serializers.CharField(max_length=120, required=False, allow_blank=True, write_only=True)

    class Meta:
        model = ContactInquiry
        fields = ["id", "name", "mobile", "email", "message", "service",
                  "service_slug", "language", "status", "created_at"]
        read_only_fields = ["id", "service_slug", "status", "created_at"]

    def validate_language(self, value):
        value = (value or "fa").strip().lower()
        if value not in ("fa", "en"):
            value = "fa"
        return value

    def validate(self, attrs):
        service = attrs.pop("service", "").strip() if attrs.get("service") else ""
        if service and not attrs.get("service_slug"):
            attrs["service_slug"] = service
        if not attrs.get("language"):
            attrs["language"] = "fa"
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("service", None)
        return data
