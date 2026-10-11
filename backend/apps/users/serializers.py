from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .services import MAX_CODE_LENGTH, MIN_CODE_LENGTH, normalize_mobile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username", "mobile", "first_name", "last_name")
        read_only_fields = ("id",)

    def validate_mobile(self, value):
        try:
            return normalize_mobile(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "username", "password", "mobile", "first_name", "last_name")

    def validate_mobile(self, value):
        try:
            return normalize_mobile(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class MobileCodeRequestSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=20)

    def validate_mobile(self, value):
        try:
            return normalize_mobile(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class MobileCodeVerifySerializer(MobileCodeRequestSerializer):
    code = serializers.CharField(
        min_length=MIN_CODE_LENGTH,
        max_length=MAX_CODE_LENGTH,
        trim_whitespace=True,
    )

    def validate_code(self, value):
        code_length = getattr(settings, "OTP_CODE_LENGTH", 5)
        if not MIN_CODE_LENGTH <= code_length <= MAX_CODE_LENGTH:
            raise serializers.ValidationError("OTP_CODE_LENGTH is misconfigured.")
        if len(value) != code_length or not value.isascii() or not value.isdecimal():
            raise serializers.ValidationError(
                f"Enter the {code_length}-digit login code."
            )
        return value
