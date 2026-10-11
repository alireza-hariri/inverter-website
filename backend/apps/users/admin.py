from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MobileLoginCode, User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "mobile", "username", "is_staff", "is_active")
    ordering = ("email",)
    fieldsets = UserAdmin.fieldsets + (("Mobile login", {"fields": ("mobile",)}),)


@admin.register(MobileLoginCode)
class MobileLoginCodeAdmin(admin.ModelAdmin):
    list_display = ("mobile", "created_at", "expires_at", "attempts", "consumed_at")
    readonly_fields = ("mobile", "code_hash", "created_at", "expires_at", "attempts", "consumed_at")
