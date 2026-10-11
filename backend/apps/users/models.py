from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    # Stored in canonical Iranian format (for example, 09123456789). It is
    # nullable so existing email/password accounts and admin users continue to
    # work without a phone number.
    mobile = models.CharField(max_length=20, unique=True, blank=True, null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    def __str__(self): return self.email


class MobileLoginCode(models.Model):
    mobile = models.CharField(max_length=20, db_index=True)
    code_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    consumed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ("-created_at",)
        # Named explicitly so the migration cannot drift from the model the way
        # an auto-generated hash name does.
        indexes = [models.Index(fields=("mobile", "created_at"), name="users_mobile_created_idx")]

    def __str__(self):
        return f"Mobile login for {self.mobile}"
