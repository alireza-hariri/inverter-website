import logging

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

from apps.content.backups import available_backups, create_backup, restore_backup
from apps.content.models import Article, Brand, FaqItem, Service

logger = logging.getLogger(__name__)


def _can_view_backups(user):
    return user.is_superuser or all(
        user.has_perm(f"content.view_{model._meta.model_name}")
        for model in (Article, Brand, FaqItem, Service)
    )


def _can_restore_backups(user):
    return user.is_superuser or all(
        user.has_perm(f"content.{action}_{model._meta.model_name}")
        for model in (Article, Brand, FaqItem, Service)
        for action in ("view", "add", "change", "delete")
    )


@require_http_methods(["GET", "POST"])
def content_backups(request):
    if not _can_view_backups(request.user):
        raise PermissionDenied

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "export":
            try:
                saved = create_backup()
            except OSError:
                messages.error(request, "فایل پشتیبان ذخیره نشد؛ دسترسی نوشتن پوشه را بررسی کنید.")
            else:
                messages.success(request, f"پشتیبان ساخته شد: {saved.name}")
        elif action == "restore":
            if not _can_restore_backups(request.user):
                messages.error(request, "مجوز لازم برای بارگذاری و جایگزینی محتوا را ندارید.")
            elif request.POST.get("confirm_replace") != "yes":
                messages.error(request, "برای بارگذاری باید جایگزینی محتوای فعلی را تأیید کنید.")
            else:
                try:
                    count = restore_backup(request.POST.get("filename", ""))
                except ValueError as exc:
                    messages.error(request, str(exc))
                except Exception:
                    logger.exception("Failed to restore content backup %s", request.POST.get("filename", ""))
                    messages.error(request, "بارگذاری انجام نشد؛ فایل بررسی شد و هیچ تغییری ذخیره نشد.")
                else:
                    messages.success(request, f"محتوا با موفقیت از پشتیبان بارگذاری شد ({count} رکورد).")

        redirect_to = request.POST.get("next", "")
        if not url_has_allowed_host_and_scheme(redirect_to, allowed_hosts={request.get_host()}):
            redirect_to = reverse("content-backups")
        return HttpResponseRedirect(redirect_to)

    context = admin.site.each_context(request)
    context.update({
        "title": "پشتیبان‌گیری محتوا",
        "backups": available_backups(),
        "can_restore": _can_restore_backups(request.user),
    })
    return render(request, "admin/content_backups.html", context)
