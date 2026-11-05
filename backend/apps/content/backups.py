"""Local, versionable snapshots of the site's editorial content."""

import json
import logging
import re
from itertools import chain
from pathlib import Path

from django.conf import settings
from django.core import serializers
from django.core.management.color import no_style
from django.db import connection, transaction
from django.db.models import Model
from django.utils import timezone

from apps.content.models import Article, Brand, FaqItem, Service


FORMAT = "electrogold-content-backup"
VERSION = 1
MAX_BACKUP_BYTES = 20 * 1024 * 1024
FILENAME_RE = re.compile(r"^content-\d{8}-\d{6}-\d{6}\.json$")
CONTENT_MODELS: tuple[type[Model], ...] = (Service, Brand, Article, FaqItem)
MODEL_BY_LABEL = {model._meta.label_lower: model for model in CONTENT_MODELS}
logger = logging.getLogger(__name__)


def backup_directory() -> Path:
    """The generated snapshots live in the local repo and can be committed normally."""
    return Path(getattr(settings, "CONTENT_EXPORT_DIR", settings.BASE_DIR / "content_exports"))


def create_backup() -> Path:
    folder = backup_directory()
    folder.mkdir(parents=True, exist_ok=True)
    rows = chain(*(model.objects.order_by("pk") for model in CONTENT_MODELS))
    payload = {
        "format": FORMAT,
        "version": VERSION,
        "exported_at": timezone.now().isoformat(),
        "includes": [model._meta.label_lower for model in CONTENT_MODELS],
        "records": json.loads(serializers.serialize("json", rows)),
    }
    stamp = timezone.localtime().strftime("%Y%m%d-%H%M%S-%f")
    destination = folder / f"content-{stamp}.json"
    temporary = folder / f".{destination.name}.tmp"
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(destination)
    return destination


def available_backups() -> list[dict]:
    folder = backup_directory()
    if not folder.is_dir():
        return []

    result = []
    for path in sorted(folder.iterdir(), reverse=True):
        if not FILENAME_RE.fullmatch(path.name) or not path.is_file():
            continue
        try:
            if path.resolve().parent != folder.resolve():
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if (not isinstance(payload, dict) or payload.get("format") != FORMAT
                or payload.get("version") != VERSION):
            continue
        result.append({
            "name": path.name,
            "size": path.stat().st_size,
            "exported_at": payload.get("exported_at", ""),
            "count": len(payload.get("records", [])) if isinstance(payload.get("records"), list) else 0,
        })
    return result


def _read_backup(filename: str) -> tuple[Path, list]:
    if not FILENAME_RE.fullmatch(filename):
        raise ValueError("نام فایل پشتیبان معتبر نیست.")
    folder = backup_directory().resolve()
    path = (folder / filename).resolve()
    if path.parent != folder or not path.is_file():
        raise ValueError("فایل پشتیبان پیدا نشد.")
    if path.stat().st_size > MAX_BACKUP_BYTES:
        raise ValueError("حجم فایل پشتیبان بیش از حد مجاز است.")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("فایل پشتیبان JSON معتبر نیست.") from exc
    if (not isinstance(payload, dict) or payload.get("format") != FORMAT
            or payload.get("version") != VERSION):
        raise ValueError("فرمت یا نسخهٔ فایل پشتیبان پشتیبانی نمی‌شود.")
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("فایل پشتیبان خالی یا نامعتبر است؛ برای جلوگیری از پاک‌شدن محتوا بارگذاری نشد.")
    if len(records) > 50_000:
        raise ValueError("تعداد رکوردهای فایل پشتیبان بیش از حد مجاز است.")

    for record in records:
        if not isinstance(record, dict) or record.get("model") not in MODEL_BY_LABEL:
            raise ValueError("فایل شامل نوع داده‌ای خارج از محدودهٔ پشتیبان محتواست.")
    try:
        deserialized = list(serializers.deserialize("json", json.dumps(records, ensure_ascii=False)))
    except Exception as exc:
        raise ValueError("ساختار یکی از رکوردهای فایل پشتیبان معتبر نیست.") from exc
    if not deserialized:
        raise ValueError("فایل پشتیبان رکورد قابل‌بازیابی ندارد.")

    order = {model._meta.label_lower: index for index, model in enumerate(CONTENT_MODELS)}
    deserialized.sort(key=lambda item: order[item.object._meta.label_lower])
    return path, deserialized


def restore_backup(filename: str) -> int:
    """Replace the four editorial tables atomically; leave users, inquiries and SEO settings alone."""
    _, objects = _read_backup(filename)
    with transaction.atomic():
        # Remove dependants before their referenced records.
        FaqItem.objects.all().delete()
        Article.objects.all().delete()
        Brand.objects.all().delete()
        Service.objects.all().delete()
        for item in objects:
            item.save()
        # Keep auto-increment sequences valid on databases that need an explicit reset.
        with connection.cursor() as cursor:
            for sql in connection.ops.sequence_reset_sql(no_style(), CONTENT_MODELS):
                cursor.execute(sql)
    return len(objects)
