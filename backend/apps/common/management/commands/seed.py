
"""Idempotent seed data: demo accounts, plus whatever this site's models need.

Rerunnable by design. Every write is an upsert keyed on something stable (a
user email, a slug), so a second run updates the rows the first run made
instead of adding a parallel set. What a running site owns -- passwords, and
anything an editor has since changed -- is left alone unless `--fresh` says
otherwise.

This backend ships without a product catalogue, so the command starts with the
demo accounts only. Add this site's own data here: define the records as module
level constants, write a `seed_<thing>` method that upserts them keyed on a
stable field, and call it from `handle` inside the existing transaction. Use
`self.find_images` for pictures -- it is already wired to the image finder and
degrades to leaving a record's current image alone when the service is down.

Make each constant the whole truth about its model, not an addition to it. The
command runs again on a database that already holds the last run's rows, so a
`seed_<thing>` that only upserts leaves anything it stopped defining behind,
serving forever. Retire those in the same method: delete the rows your keys no
longer name, and where a protected relation forbids deleting one, take it out
of circulation instead (an `is_active`-style flag) so history survives but the
site stops showing it.
"""

import html
import json
from pathlib import Path
import requests
from django.conf import settings as app_settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.common.management.commands.delta_error_articles import DELTA_ERROR_ARTICLES, DELTA_OV_ARTICLE_SOURCE
from apps.common.management.commands.siemens_error_articles import SIEMENS_ERROR_ARTICLES
from apps.common.management.commands.yaskawa_error_articles import YASKAWA_ERROR_ARTICLES
from apps.common.management.commands.schneider_error_articles import SCHNEIDER_ERROR_ARTICLES
from apps.common.management.commands.growatt_error_articles import GROWATT_ERROR_ARTICLES
from apps.common.management.commands.invt_error_articles import INVT_ERROR_ARTICLES
from apps.common.management.commands.solarx_error_articles import SOLARX_ERROR_ARTICLES
from apps.common.management.commands.comparison_articles import GENERAL_COMPARISON_ARTICLES
from apps.common.management.commands.elevator_service_content import ELEVATOR_SERVICE_BODY_EN, ELEVATOR_SERVICE_BODY_FA
from apps.common.management.commands.industrial_service_content import INDUSTRIAL_SERVICE_BODY_EN, INDUSTRIAL_SERVICE_BODY_FA
from apps.common.management.commands.solar_service_content import SOLAR_SERVICE_BODY_EN, SOLAR_SERVICE_BODY_FA

# Used when a record's own query comes back empty, so that every seeded record
# still ends up with an image. Reword it for this site's subject matter.
# This is a finished ElectroGold catalogue, not the generic template data.
SEED_DATA_IS_PLACEHOLDER = False
FALLBACK_IMAGE_QUERY = "industrial inverter repair technician"

# Reliable, freely hotlinkable editorial images used when the local finder is
# unavailable. They are intentionally shared by related records, avoiding a
# network request for every card while ensuring no public card is blank.
SERVICE_IMAGE_URLS = {
    "elevator-inverter-repair": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=1200&q=80",
    "industrial-inverter-repair": "https://images.unsplash.com/photo-1565610222536-ef125c59da2e?w=1200&q=80",
    "solar-inverter-repair": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=1200&q=80",
}
BRAND_LOGO_PATHS = {
    "siemens": "/brands/siemens.svg",
    "schneider": "/brands/schneider.svg",
    "ls": "/brands/ls.svg",
    "fuji": "/brands/fuji.svg",
    "danfoss": "/brands/danfoss.svg",
    "abb": "/brands/abb.svg",
    "sbt": "/brands/sbt.svg",
    "kyuma": "/brands/qma.svg",
    "solarx": "/brands/solarx.svg",
    "voltronic": "/brands/voltronic.svg",
    "sma": "/brands/sma.svg",
    "fronius": "/brands/fronius.svg",
    "huawei": "/brands/huawei.svg",
    "sungrow": "/brands/sungrow.svg",
    "goodwe": "/brands/goodwe.svg",
    "solis": "/brands/solis.svg",
    "sofar": "/brands/sofar.svg",
    "must": "/brands/must.svg",
    "yaskawa": "/brands/yaskawa.svg",
    "monarch": "/brands/monarch.svg",
    "hpmont": "/brands/hpmont.svg",
    "zilabeg": "/brands/zilabeg.svg",
    "delta": "/brands/delta.svg",
    "inovance": "/brands/inovance.svg",
    "growatt": "/brands/growatt.svg",
}
# Image written by the former one-photo-for-every-article fallback. Replace it
# with the locally hosted, topic-matched repair photos below.
LEGACY_ARTICLE_IMAGE_URL = "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=1200&q=80"
PREVIOUS_ARTICLE_IMAGE_PATHS = {
    "/articles/drive-repair-workbench.webp",
    "/articles/elevator-drive-service.webp",
    "/articles/industrial-vfd-testing.webp",
    "/articles/solar-inverter-diagnostics.webp",
    "/articles/inverter-board-inspection.webp",
    "/articles/industrial-panel-multimeter.webp",
    "/articles/open-switchboard-repair.webp",
    "/articles/control-panel-technician.webp",
    "/articles/elevator-machine-room.webp",
    "/articles/drive-board-soldering.webp",
    "/articles/drive-board-testing.webp",
    "/articles/drive-board-repair.webp",
    "/articles/solar-inverter-service.webp",
    "/articles/solar-inverter-outdoor.webp",
}
ARTICLE_IMAGE_MANIFEST = json.loads(
    Path(__file__).with_name("article_image_manifest.json").read_text(encoding="utf-8")
)


def article_image_path(record):
    """Return this article's individually assigned, locally hosted photo."""
    return ARTICLE_IMAGE_MANIFEST[record["slug"]]["path"]

SERVICES = [
    {"slug": "elevator-inverter-repair", "category": "elevator",
     "title_fa": "خدمات اینورتر آسانسور", "title_en": "Elevator Inverter Services",
     "summary_fa": "تعمیر تخصصی و بازسازی اینورترهای آسانسور؛ عیب‌یابی خطاهای کنترلی، انکودر، برد قدرت و سیستم ترمز.",
     "summary_en": "Specialist elevator-inverter repair and reconditioning, including control, encoder, power-stage and braking diagnostics.",
     "body_fa": ELEVATOR_SERVICE_BODY_FA,
     "body_en": ELEVATOR_SERVICE_BODY_EN,
     "seo_title_fa": "تعمیر تخصصی و بازسازی اینورتر آسانسور | الکتروگلد", "seo_title_en": "Specialist Elevator Inverter Repair | ElectroGold",
     "seo_description_fa": "تعمیر و بازسازی تخصصی اینورتر آسانسور با عیب‌یابی برد قدرت و کنترل، بررسی انکودر، ترمز و تست زیر بار.",
     "seo_description_en": "Specialist elevator-drive repair and reconditioning with control, encoder and braking diagnostics plus load testing.",
     "image_query": "elevator control panel inverter repair"},
    {"slug": "industrial-inverter-repair", "category": "industrial",
     "title_fa": "خدمات درایوهای صنعتی", "title_en": "Industrial Drive Services",
     "summary_fa": "تعمیر و بازسازی تخصصی درایوهای صنعتی برای افزایش پایداری و کاهش توقف خط تولید.",
     "summary_en": "Specialist industrial-drive repair and reconditioning to improve reliability and reduce production downtime.",
     "body_fa": INDUSTRIAL_SERVICE_BODY_FA,
     "body_en": INDUSTRIAL_SERVICE_BODY_EN,
     "seo_title_fa": "تعمیر تخصصی و بازسازی درایوهای صنعتی | الکتروگلد", "seo_title_en": "Industrial Drive Repair & Reconditioning | ElectroGold",
     "seo_description_fa": "عیب‌یابی نویز، بازسازی برد قدرت، تنظیم کنترل و رفع خطاهای ارتباطی در درایوهای صنعتی.",
     "seo_description_en": "Industrial drive diagnostics, power-stage reconditioning, control tuning and fieldbus communication repair.",
     "image_query": "industrial variable frequency drive factory"},
    {"slug": "solar-inverter-repair", "category": "solar",
     "title_fa": "خدمات نیروگاه‌های خورشیدی/سانورتر", "title_en": "Solar Power Plant & Inverter Services",
     "summary_fa": "تعمیر تخصصی و بهینه‌سازی سانورتر، MPPT، مدارهای DC/AC، مانیتورینگ و حفاظت نیروگاه خورشیدی.",
     "summary_en": "Specialist solar-inverter optimization, MPPT, DC/AC circuit, monitoring and solar-plant protection services.",
     "body_fa": SOLAR_SERVICE_BODY_FA,
     "body_en": SOLAR_SERVICE_BODY_EN,
     "seo_title_fa": "تعمیر و بهینه‌سازی سانورتر و اینورتر خورشیدی | الکتروگلد", "seo_title_en": "Solar Inverter Repair & Optimization | ElectroGold",
     "seo_description_fa": "تعمیر و بهینه‌سازی سانورتر با عیب‌یابی MPPT، مدارهای DC/AC، مانیتورینگ و حفاظت در برابر نوسانات شبکه.",
     "seo_description_en": "Solar-inverter service with MPPT, DC/AC, monitoring and surge-protection diagnostics.",
     "image_query": "solar inverter installation panels"},
]

BRANDS = [
    {"slug": "yaskawa", "category": "elevator", "name_fa": "یاسکاوا", "name_en": "Yaskawa",
     "description_fa": "تعمیر اینورتر یاسکاوا آسانسور و صنعتی.", "description_en": "Yaskawa elevator and industrial inverter repair.",
     "content_fa": "پشتیبانی کامل درایوهای یاسکاوا.", "content_en": "Full support for Yaskawa drives.",
     "seo_title_fa": "تعمیر اینورتر یاسکاوا | الکتروگلد", "seo_title_en": "Yaskawa Inverter Repair | ElectroGold",
     "seo_description_fa": "عیب‌یابی و تعمیر اینورتر یاسکاوا.", "seo_description_en": "Yaskawa inverter diagnostics and repair.",
     "image_query": "yaskawa inverter drive", "services": ["elevator-inverter-repair", "industrial-inverter-repair"]},
    {"slug": "monarch", "category": "elevator", "name_fa": "مونارک", "name_en": "Monarch",
     "description_fa": "تعمیر اینورتر مونارک آسانسور.", "description_en": "Monarch elevator inverter repair.",
     "content_fa": "تعمیر کنترلرهای مونارک.", "content_en": "Monarch controller repair.",
     "seo_title_fa": "تعمیر اینورتر مونارک | الکتروگلد", "seo_title_en": "Monarch Inverter Repair | ElectroGold",
     "seo_description_fa": "عیب‌یابی و تعمیر مونارک.", "seo_description_en": "Monarch diagnostics and repair.",
     "image_query": "elevator inverter controller cabinet", "services": ["elevator-inverter-repair"]},
    {"slug": "hpmont", "category": "elevator", "name_fa": "اچ‌پی‌مونت", "name_en": "HPMont",
     "description_fa": "تعمیر اینورتر اچ‌پی‌مونت.", "description_en": "HPMont inverter repair.",
     "content_fa": "پشتیبانی درایوهای HPMont.", "content_en": "HPMont drive support.",
     "seo_title_fa": "تعمیر اینورتر اچ‌پی‌مونت | الکتروگلد", "seo_title_en": "HPMont Inverter Repair | ElectroGold",
     "seo_description_fa": "عیب‌یابی و تعمیر اچ‌پی‌مونت.", "seo_description_en": "HPMont diagnostics and repair.",
     "image_query": "elevator machine room equipment", "services": ["elevator-inverter-repair"]},
    {"slug": "zilabeg", "category": "elevator", "name_fa": "زیلابگ", "name_en": "Zilabeg",
     "description_fa": "تعمیر تجهیزات زیلابگ.", "description_en": "Zilabeg equipment repair.",
     "content_fa": "سرویس موتور و درایو زیلابگ.", "content_en": "Zilabeg motor and drive service.",
     "seo_title_fa": "تعمیر زیلابگ | الکتروگلد", "seo_title_en": "Zilabeg Repair | ElectroGold",
     "seo_description_fa": "عیب‌یابی و تعمیر زیلابگ.", "seo_description_en": "Zilabeg diagnostics and repair.",
     "image_query": "elevator motor machine", "services": ["elevator-inverter-repair"]},
    {"slug": "delta", "category": "industrial", "name_fa": "دلتا", "name_en": "Delta",
     "description_fa": "تعمیر اینورتر دلتا.", "description_en": "Delta inverter repair.",
     "content_fa": "تعمیر درایوهای دلتا.", "content_en": "Delta drive repair.",
     "seo_title_fa": "تعمیر اینورتر دلتا | الکتروگلد", "seo_title_en": "Delta Inverter Repair | ElectroGold",
     "seo_description_fa": "عیب‌یابی و تعمیر دلتا.", "seo_description_en": "Delta diagnostics and repair.",
      "image_query": "delta industrial drive panel", "services": ["elevator-inverter-repair", "industrial-inverter-repair"]},
    {"slug": "inovance", "category": "industrial", "name_fa": "اینوونس", "name_en": "Inovance",
     "description_fa": "تعمیر درایوهای صنعتی و آسانسوری اینوونس.", "description_en": "Inovance industrial and elevator drive repair.",
     "content_fa": "پشتیبانی فنی درایوهای Inovance در کاربردهای صنعتی و آسانسوری.", "content_en": "Technical support for Inovance drives in industrial and elevator applications.",
     "seo_title_fa": "تعمیر اینورتر اینوونس | الکتروگلد", "seo_title_en": "Inovance Inverter Repair | ElectroGold",
      "seo_description_fa": "عیب‌یابی و تعمیر درایوهای صنعتی و آسانسوری اینوونس.", "seo_description_en": "Diagnostics and repair for Inovance industrial and elevator drives.",
      "image_query": "industrial automation control panel", "services": ["industrial-inverter-repair", "elevator-inverter-repair"]},
    {"slug": "growatt", "category": "solar", "name_fa": "گرووات", "name_en": "Growatt",
     "description_fa": "تعمیر سانورتر گرووات.", "description_en": "Growatt solar inverter repair.",
     "content_fa": "سرویس سانورترهای Growatt.", "content_en": "Growatt inverter service.",
     "seo_title_fa": "تعمیر سانورتر گرووات | الکتروگلد", "seo_title_en": "Growatt Inverter Repair | ElectroGold",
      "seo_description_fa": "عیب‌یابی و تعمیر گرووات.", "seo_description_en": "Growatt diagnostics and repair.",
      "image_query": "growatt solar inverter wall", "services": ["solar-inverter-repair"]},
    {"slug": "siemens", "category": "elevator", "name_fa": "زیمنس", "name_en": "Siemens",
     "description_fa": "پشتیبانی و تعمیر درایوهای زیمنس در کاربردهای آسانسوری و صنعتی.", "description_en": "Siemens drive repair and support for elevator and industrial applications.",
     "content_fa": "عیب‌یابی خطاهای درایو و تعمیر بردهای قدرت و کنترل زیمنس.", "content_en": "Diagnosis of Siemens drive faults and repair of power and control boards.",
     "seo_title_fa": "تعمیر درایو زیمنس | الکتروگلد", "seo_title_en": "Siemens Drive Repair | ElectroGold",
      "seo_description_fa": "خدمات عیب‌یابی و تعمیر درایوهای زیمنس برای آسانسور و صنعت.", "seo_description_en": "Diagnostics and repair for Siemens elevator and industrial drives.",
      "image_query": "Siemens elevator inverter drive", "services": ["elevator-inverter-repair", "industrial-inverter-repair"]},
    {"slug": "schneider", "category": "industrial", "name_fa": "اشنایدر", "name_en": "Schneider",
      "description_fa": "خدمات عیب‌یابی و تعمیر درایوهای اشنایدر در کاربردهای صنعتی.", "description_en": "Diagnostics and repair for Schneider drives in industrial applications.",
      "content_fa": "پشتیبانی فنی درایوهای اشنایدر و تعمیر بردهای قدرت و کنترل.", "content_en": "Technical support for Schneider drives and repair of power and control boards.",
      "seo_title_fa": "تعمیر درایو اشنایدر | الکتروگلد", "seo_title_en": "Schneider Drive Repair | ElectroGold",
      "seo_description_fa": "عیب‌یابی خطاها و تعمیر تخصصی درایوهای اشنایدر.", "seo_description_en": "Fault diagnosis and specialist repair for Schneider drives.",
      "image_query": "Schneider Altivar industrial drive", "services": ["industrial-inverter-repair"]},
    {"slug": "ls", "category": "elevator", "name_fa": "ال‌اس", "name_en": "LS",
     "description_fa": "خدمات عیب‌یابی و تعمیر درایوهای ال‌اس.", "description_en": "LS drive diagnostics and repair services.",
     "content_fa": "پشتیبانی فنی و تعمیر درایوهای ال‌اس در کاربردهای آسانسوری.", "content_en": "Technical support and repair for LS drives in elevator applications.",
     "seo_title_fa": "تعمیر درایو ال‌اس | الکتروگلد", "seo_title_en": "LS Drive Repair | ElectroGold",
     "seo_description_fa": "عیب‌یابی و تعمیر تخصصی درایوهای آسانسوری ال‌اس.", "seo_description_en": "Specialist diagnostics and repair for LS elevator drives.",
     "image_query": "LS elevator inverter drive", "services": ["elevator-inverter-repair"]},
    {"slug": "fuji", "category": "elevator", "name_fa": "فوجی", "name_en": "Fuji Electric",
     "description_fa": "خدمات تخصصی درایوهای فوجی برای کاربردهای آسانسوری.", "description_en": "Specialist Fuji drive services for elevator applications.",
     "content_fa": "عیب‌یابی و تعمیر درایوهای فوجی و بررسی مدارات قدرت و کنترل.", "content_en": "Fuji drive diagnostics and repair, including power and control circuit checks.",
     "seo_title_fa": "تعمیر درایو فوجی | الکتروگلد", "seo_title_en": "Fuji Drive Repair | ElectroGold",
     "seo_description_fa": "عیب‌یابی و تعمیر درایوهای فوجی در سیستم‌های آسانسوری.", "seo_description_en": "Diagnostics and repair for Fuji drives used in elevator systems.",
     "image_query": "Fuji Electric elevator inverter", "services": ["elevator-inverter-repair"]},
    {"slug": "danfoss", "category": "elevator", "name_fa": "دانفوس", "name_en": "Danfoss",
     "description_fa": "پشتیبانی و تعمیر درایوهای دانفوس برای آسانسور و صنعت.", "description_en": "Danfoss drive support and repair for elevator and industrial applications.",
     "content_fa": "عیب‌یابی تخصصی و تعمیر بردهای کنترل و قدرت درایو دانفوس.", "content_en": "Specialist diagnostics and repair for Danfoss drive control and power boards.",
     "seo_title_fa": "تعمیر درایو دانفوس | الکتروگلد", "seo_title_en": "Danfoss Drive Repair | ElectroGold",
     "seo_description_fa": "خدمات تعمیر و عیب‌یابی درایوهای دانفوس در کاربردهای آسانسوری.", "seo_description_en": "Danfoss drive diagnostics and repair for elevator applications.",
     "image_query": "Danfoss elevator drive inverter", "services": ["elevator-inverter-repair"]},
    {"slug": "abb", "category": "elevator", "name_fa": "ای‌بی‌بی", "name_en": "ABB",
     "description_fa": "خدمات عیب‌یابی و تعمیر درایوهای ای‌بی‌بی.", "description_en": "ABB drive diagnostics and repair services.",
     "content_fa": "بررسی و تعمیر تخصصی مدارات قدرت و کنترل درایوهای ABB.", "content_en": "Specialist inspection and repair of ABB drive power and control circuits.",
     "seo_title_fa": "تعمیر درایو ABB | الکتروگلد", "seo_title_en": "ABB Drive Repair | ElectroGold",
     "seo_description_fa": "عیب‌یابی درایوهای ای‌بی‌بی در سیستم‌های آسانسوری، صنعتی و خورشیدی.", "seo_description_en": "ABB drive diagnostics for elevator, industrial and solar systems.",
      "image_query": "ABB elevator inverter drive", "services": ["elevator-inverter-repair", "industrial-inverter-repair", "solar-inverter-repair"]},
    {"slug": "sbt", "category": "elevator", "name_fa": "اس‌بی‌تی", "name_en": "SBT",
     "description_fa": "خدمات تخصصی و تعمیر درایوهای اس‌بی‌تی.", "description_en": "Specialist service and repair for SBT drives.",
     "content_fa": "عیب‌یابی و تعمیر درایوهای SBT در کاربردهای آسانسوری.", "content_en": "Diagnostics and repair for SBT drives in elevator applications.",
     "seo_title_fa": "تعمیر درایو SBT | الکتروگلد", "seo_title_en": "SBT Drive Repair | ElectroGold",
     "seo_description_fa": "خدمات تعمیر و عیب‌یابی درایوهای اس‌بی‌تی.", "seo_description_en": "SBT drive troubleshooting and repair services.",
     "image_query": "SBT elevator drive inverter", "services": ["elevator-inverter-repair"]},
    {"slug": "kyuma", "category": "elevator", "name_fa": "QMA", "name_en": "QMA",
     "description_fa": "خدمات تعمیر و پشتیبانی درایوهای QMA.", "description_en": "Repair and technical support for QMA drives.",
     "content_fa": "عیب‌یابی و تعمیر درایوهای QMA در کاربردهای آسانسوری.", "content_en": "Diagnostics and repair for QMA drives in elevator applications.",
     "seo_title_fa": "تعمیر درایو QMA | الکتروگلد", "seo_title_en": "QMA Drive Repair | ElectroGold",
      "seo_description_fa": "خدمات فنی و عیب‌یابی درایوهای QMA.", "seo_description_en": "Technical service and diagnostics for QMA drives.",
      "image_query": "QMA elevator drive inverter", "services": ["elevator-inverter-repair"]},
    {"slug": "solarx", "category": "solar", "name_fa": "سولارکس", "name_en": "SolarX",
      "description_fa": "عیب‌یابی و خدمات اینورترهای خورشیدی سولارکس.", "description_en": "SolarX solar-inverter diagnostics and service.",
      "content_fa": "پشتیبانی فنی و عیب‌یابی تجهیزات خورشیدی سولارکس.", "content_en": "Technical support and diagnostics for SolarX solar equipment.",
      "seo_title_fa": "تعمیر اینورتر سولارکس | الکتروگلد", "seo_title_en": "SolarX Inverter Service | ElectroGold",
      "seo_description_fa": "خدمات فنی و عیب‌یابی اینورترهای خورشیدی سولارکس.", "seo_description_en": "Technical service and troubleshooting for SolarX solar inverters.",
      "image_query": "SolarX solar inverter", "services": ["solar-inverter-repair"]},
    {"slug": "voltronic", "category": "solar", "name_fa": "ولت‌رونیک", "name_en": "Voltronic",
      "description_fa": "خدمات و عیب‌یابی سانورترهای ولت‌رونیک.", "description_en": "Voltronic inverter service and diagnostics.",
      "content_fa": "پشتیبانی فنی سانورترها و اینورترهای خورشیدی ولت‌رونیک.", "content_en": "Technical support for Voltronic solar inverters and inverter-chargers.",
      "seo_title_fa": "تعمیر سانورتر ولت‌رونیک | الکتروگلد", "seo_title_en": "Voltronic Inverter Service | ElectroGold",
      "seo_description_fa": "عیب‌یابی و خدمات تعمیر سانورترهای ولت‌رونیک.", "seo_description_en": "Diagnostics and repair service for Voltronic inverters.",
      "image_query": "Voltronic solar inverter", "services": ["solar-inverter-repair"]},
    {"slug": "sma", "category": "solar", "name_fa": "اس‌ام‌ای", "name_en": "SMA",
      "description_fa": "عیب‌یابی و خدمات اینورترهای خورشیدی SMA.", "description_en": "SMA solar-inverter diagnostics and service.",
      "content_fa": "پشتیبانی فنی و تعمیر اینورترهای خورشیدی اس‌ام‌ای.", "content_en": "Technical support and repair for SMA solar inverters.",
      "seo_title_fa": "تعمیر اینورتر خورشیدی SMA | الکتروگلد", "seo_title_en": "SMA Solar Inverter Service | ElectroGold",
      "seo_description_fa": "خدمات عیب‌یابی و تعمیر اینورترهای خورشیدی اس‌ام‌ای.", "seo_description_en": "Diagnostics and repair services for SMA solar inverters.",
      "image_query": "SMA solar inverter", "services": ["solar-inverter-repair"]},
    {"slug": "fronius", "category": "solar", "name_fa": "فرونیوس", "name_en": "Fronius",
      "description_fa": "خدمات عیب‌یابی و تعمیر اینورترهای خورشیدی فرونیوس.", "description_en": "Fronius solar-inverter diagnostics and repair.",
      "content_fa": "پشتیبانی فنی اینورترهای فرونیوس و بررسی عملکرد سیستم خورشیدی.", "content_en": "Technical support for Fronius inverters and solar-system performance checks.",
      "seo_title_fa": "تعمیر اینورتر فرونیوس | الکتروگلد", "seo_title_en": "Fronius Inverter Service | ElectroGold",
      "seo_description_fa": "عیب‌یابی و تعمیر تخصصی اینورترهای خورشیدی فرونیوس.", "seo_description_en": "Specialist troubleshooting and repair for Fronius solar inverters.",
       "image_query": "Fronius solar inverter", "services": ["solar-inverter-repair"]},
    {"slug": "huawei", "category": "solar", "name_fa": "هوآوی", "name_en": "Huawei",
      "description_fa": "خدمات فنی و عیب‌یابی اینورترهای خورشیدی هوآوی.", "description_en": "Huawei solar-inverter technical service and diagnostics.",
      "content_fa": "پشتیبانی و عیب‌یابی اینورترهای خورشیدی هوآوی.", "content_en": "Support and diagnostics for Huawei solar inverters.",
      "seo_title_fa": "تعمیر اینورتر خورشیدی هوآوی | الکتروگلد", "seo_title_en": "Huawei Solar Inverter Service | ElectroGold",
      "seo_description_fa": "خدمات عیب‌یابی و تعمیر اینورترهای خورشیدی هوآوی.", "seo_description_en": "Diagnostics and repair services for Huawei solar inverters.",
      "image_query": "Huawei solar inverter", "services": ["solar-inverter-repair"]},
    {"slug": "sungrow", "category": "solar", "name_fa": "سانگرو", "name_en": "Sungrow",
      "description_fa": "خدمات تعمیر و نگهداری اینورترهای خورشیدی سانگرو.", "description_en": "Sungrow solar-inverter repair and maintenance.",
      "content_fa": "عیب‌یابی و پشتیبانی اینورترهای سانگرو و تجهیزات نیروگاه خورشیدی.", "content_en": "Diagnostics and support for Sungrow inverters and solar-plant equipment.",
      "seo_title_fa": "تعمیر اینورتر سانگرو | الکتروگلد", "seo_title_en": "Sungrow Inverter Service | ElectroGold",
      "seo_description_fa": "خدمات عیب‌یابی و تعمیر اینورترهای خورشیدی سانگرو.", "seo_description_en": "Diagnostics and repair services for Sungrow solar inverters.",
      "image_query": "Sungrow solar inverter", "services": ["solar-inverter-repair"]},
    {"slug": "goodwe", "category": "solar", "name_fa": "گودوی", "name_en": "GoodWe",
      "description_fa": "عیب‌یابی و خدمات اینورترهای خورشیدی گودوی.", "description_en": "GoodWe solar-inverter diagnostics and service.",
      "content_fa": "پشتیبانی فنی و تعمیر اینورترهای گودوی.", "content_en": "Technical support and repair for GoodWe inverters.",
      "seo_title_fa": "تعمیر اینورتر گودوی | الکتروگلد", "seo_title_en": "GoodWe Inverter Service | ElectroGold",
      "seo_description_fa": "خدمات تخصصی عیب‌یابی و تعمیر اینورترهای خورشیدی گودوی.", "seo_description_en": "Specialist diagnostics and repair for GoodWe solar inverters.",
      "image_query": "GoodWe solar inverter", "services": ["solar-inverter-repair"]},
    {"slug": "solis", "category": "solar", "name_fa": "سولیس", "name_en": "Solis",
      "description_fa": "خدمات عیب‌یابی و تعمیر اینورترهای خورشیدی سولیس.", "description_en": "Solis solar-inverter diagnostics and repair.",
      "content_fa": "پشتیبانی فنی و تعمیر سانورترها و اینورترهای سولیس.", "content_en": "Technical support and repair for Solis solar inverters.",
      "seo_title_fa": "تعمیر اینورتر سولیس | الکتروگلد", "seo_title_en": "Solis Inverter Service | ElectroGold",
      "seo_description_fa": "عیب‌یابی و خدمات تخصصی اینورترهای سولیس.", "seo_description_en": "Specialist troubleshooting and service for Solis inverters.",
      "image_query": "Solis solar inverter", "services": ["solar-inverter-repair"]},
    {"slug": "sofar", "category": "solar", "name_fa": "سوفار", "name_en": "Sofar",
      "description_fa": "خدمات فنی اینورترها و سانورترهای خورشیدی سوفار.", "description_en": "Technical service for Sofar solar inverters.",
      "content_fa": "عیب‌یابی و پشتیبانی اینورترهای خورشیدی سوفار.", "content_en": "Diagnostics and support for Sofar solar inverters.",
      "seo_title_fa": "تعمیر اینورتر سوفار | الکتروگلد", "seo_title_en": "Sofar Inverter Service | ElectroGold",
      "seo_description_fa": "خدمات عیب‌یابی و تعمیر اینورترهای خورشیدی سوفار.", "seo_description_en": "Diagnostics and repair services for Sofar solar inverters.",
      "image_query": "Sofar solar inverter", "services": ["solar-inverter-repair"]},
    {"slug": "must", "category": "solar", "name_fa": "ماست", "name_en": "MUST",
      "description_fa": "خدمات عیب‌یابی و تعمیر سانورترها و اینورترهای ماست.", "description_en": "MUST solar-inverter and inverter-charger diagnostics and repair.",
      "content_fa": "پشتیبانی فنی و تعمیر تجهیزات خورشیدی برند ماست.", "content_en": "Technical support and repair for MUST solar equipment.",
      "seo_title_fa": "تعمیر سانورتر ماست | الکتروگلد", "seo_title_en": "MUST Inverter Service | ElectroGold",
      "seo_description_fa": "عیب‌یابی و خدمات تخصصی سانورترها و اینورترهای ماست.", "seo_description_en": "Specialist diagnostics and service for MUST inverters.",
      "image_query": "MUST solar inverter", "services": ["solar-inverter-repair"]},
]
for brand in BRANDS:
    brand_name_fa = brand["name_fa"]
    brand_name_en = brand["name_en"]
    if brand["category"] == "elevator":
        brand["description_fa"] = (
            f"عیب‌یابی و تعمیر درایو آسانسوری {brand_name_fa} با بررسی خطا و تست پس از تعمیر."
        )
        brand["description_en"] = (
            f"Elevator-drive repair for {brand_name_en}, with fault diagnosis and post-repair testing."
        )
        brand["content_fa"] = (
            f"در تعمیر درایو آسانسوری {brand_name_fa}، کد خطا، شرایط توقف یا حرکت نامنظم و اتصالات بررسی می‌شود. "
            "سپس بخش‌های قدرت و کنترل متناسب با مدل عیب‌یابی می‌شوند و عملکرد درایو پیش از تحویل تست می‌شود."
        )
        brand["content_en"] = (
            f"{brand_name_en} elevator-drive repair starts with the fault code, operating symptoms and wiring checks. "
            "The power and control sections are diagnosed for the specific model, then the drive is tested before return."
        )
    elif brand["category"] == "solar":
        brand["description_fa"] = (
            f"عیب‌یابی و تعمیر اینورتر خورشیدی {brand_name_fa} با بررسی ورودی و خروجی و تست نهایی."
        )
        brand["description_en"] = (
            f"Solar-inverter repair for {brand_name_en}, with input/output diagnosis and final testing."
        )
        brand["content_fa"] = (
            f"برای تعمیر اینورتر خورشیدی {brand_name_fa}، خطاها، ورودی DC، خروجی AC و علائم افت تولید بررسی می‌شود. "
            "سپس مدارهای قدرت، کنترل و حفاظت متناسب با مدل عیب‌یابی شده و عملکرد دستگاه دوباره آزمایش می‌شود."
        )
        brand["content_en"] = (
            f"{brand_name_en} solar-inverter repair includes checking fault codes, DC input, AC output and production issues. "
            "Power, control and protection circuits are diagnosed for the model, followed by a functional test."
        )
    else:
        brand["description_fa"] = (
            f"تعمیر درایو صنعتی {brand_name_fa} با بررسی برد قدرت و کنترل و تست عملکرد."
        )
        brand["description_en"] = (
            f"Industrial-drive repair for {brand_name_en}, including power/control checks and functional testing."
        )
        brand["content_fa"] = (
            f"در تعمیر درایو صنعتی {brand_name_fa}، کد خطا، شرایط کاری و اتصالات موتور بررسی می‌شود. "
            "بردهای قدرت و کنترل و در صورت نیاز پارامترها یا ارتباطات دستگاه عیب‌یابی می‌شوند؛ سپس عملکرد درایو تست می‌شود."
        )
        brand["content_en"] = (
            f"{brand_name_en} industrial-drive repair starts with fault codes, operating conditions and motor connections. "
            "Power and control boards, and when needed parameters or communications, are checked before functional testing."
        )


BRAND_PAGE_GUIDES = {
    "siemens": {
        "intro_fa": "مدل و سری درایو روی نوع کاربرد و شیوهٔ عیب‌یابی اثر دارد. این فهرست، مدل‌های رایج و نمونه‌ای از خطاهای گزارش‌شده برای هر سری را خلاصه می‌کند.",
        "intro_en": "The drive series affects its application and diagnosis. This guide summarizes common models and example faults reported for each family.",
        "models_fa": [
            ("SINAMICS V20", "کاربری عمومی؛ فن، پمپ و نوار نقاله", "اقتصادی و پرکاربرد"),
            ("SINAMICS G120", "اتوماسیون صنعتی و کنترل دقیق", "رایج، به‌ویژه در توان‌های بالاتر"),
            ("SINAMICS G120C", "مدل فشرده با کاربردهای نزدیک به G120", "محبوب در پروژه‌های اتوماسیون"),
            ("SINAMICS S120", "سروو و سامانه‌های چندمحوره", "تخصصی و مناسب پروژه‌های پیشرفته"),
            ("MICROMASTER 440", "کاربری عمومی، نسل قدیمی", "هنوز در برخی خطوط تولید فعال است"),
            ("MICROMASTER 420", "کاربری ساده و اقتصادی، نسل قدیمی", "قطعات آن محدودتر است"),
        ],
        "models_en": [
            ("SINAMICS V20", "General use: fans, pumps and conveyors", "Economical and widely used"),
            ("SINAMICS G120", "Industrial automation and precise control", "Common, including higher-power applications"),
            ("SINAMICS G120C", "Compact drive for applications similar to G120", "Popular in automation projects"),
            ("SINAMICS S120", "Servo and multi-axis systems", "Specialist drive for advanced projects"),
            ("MICROMASTER 440", "General-purpose, older generation", "Still active in some production lines"),
            ("MICROMASTER 420", "Simple, economical, older generation", "Parts may be less available"),
        ],
        "faults_fa": [
            ("SINAMICS V20", "F0001 · اضافه‌جریان", "اتصال کوتاه خروجی یا شتاب‌گیری بسیار سریع", "بررسی موتور و کابل؛ ارزیابی IGBT در تعمیرگاه", "siemens-drive-f0001-instantaneous-overcurrent"),
            ("SINAMICS G120", "F0002 · اضافه‌ولتاژ", "انرژی برگشتی موتور یا بالا بودن ولتاژ ورودی", "بررسی مقاومت ترمز و زمان کاهش سرعت", "siemens-drive-f0002-dc-bus-overvoltage"),
            ("SINAMICS G120C", "F0003 · افت ولتاژ", "نوسان شبکه یا قطع یکی از فازهای ورودی", "بررسی ورودی و خازن‌های لینک DC", "siemens-drive-f0003-undervoltage"),
            ("SINAMICS S120", "F0004 · دمای بالای درایو", "خرابی فن، انسداد هوا یا دمای محیط بالا", "بررسی فن، هیت‌سینک و تهویه تابلو", "siemens-drive-f0004-heatsink-overtemperature"),
            ("MICROMASTER 440", "F0011 · دمای بالای موتور", "اضافه‌بار یا پارامتر نادرست موتور", "بررسی جریان و سنسور دمای PTC/KTY", "siemens-drive-f0011-motor-overtemperature"),
            ("MICROMASTER 420", "F0022 · خطای ماژول قدرت", "احتمال خرابی داخلی ماژول قدرت", "بررسی تخصصی IGBT و برد گیت‌درایو؛ مقالهٔ اختصاصی موجود نیست", None),
        ],
        "faults_en": [
            ("SINAMICS V20", "F0001 · Overcurrent", "Output short circuit or very fast acceleration", "Check motor and cable; assess IGBTs in the workshop", "siemens-drive-f0001-instantaneous-overcurrent"),
            ("SINAMICS G120", "F0002 · Overvoltage", "Regenerative motor energy or high input voltage", "Check braking resistor and deceleration time", "siemens-drive-f0002-dc-bus-overvoltage"),
            ("SINAMICS G120C", "F0003 · Undervoltage", "Supply fluctuation or a missing input phase", "Check input supply and DC-link capacitors", "siemens-drive-f0003-undervoltage"),
            ("SINAMICS S120", "F0004 · Drive overtemperature", "Fan failure, blocked airflow or high ambient temperature", "Inspect fan, heatsink and cabinet ventilation", "siemens-drive-f0004-heatsink-overtemperature"),
            ("MICROMASTER 440", "F0011 · Motor overtemperature", "Overload or incorrect motor parameters", "Check current and PTC/KTY temperature sensing", "siemens-drive-f0011-motor-overtemperature"),
            ("MICROMASTER 420", "F0022 · Power module fault", "Possible internal power-module fault", "Workshop assessment of IGBTs and gate-drive board; no dedicated article yet", None),
        ],
    },
    "delta": {
        "intro_fa": "مدل‌های دلتا از درایوهای عمومی تا سری‌های سنگین و آسانسوری را شامل می‌شوند. کدهای زیر را با مدل دقیق دستگاه و منوال همان سری تطبیق دهید.",
        "intro_en": "Delta offers general-purpose, heavy-duty and elevator drive families. Match each code below to the exact drive model and its manual.",
        "models_fa": [
            ("VFD-EL", "عمومی و سبک؛ موتورهای کوچک", "اقتصادی و پرفروش برای کاربردهای ساده"),
            ("VFD-MS300", "عمومی پیشرفته با کنترل برداری", "سری مدرن و پرکاربرد"),
            ("VFD-M", "عمومی، نسل قدیمی", "در دستگاه‌های قدیمی فراوان است"),
            ("VFD-C2000", "سنگین و گشتاور بالا", "مناسب محیط‌های صنعتی سخت"),
            ("VFD-B", "سنگین، نسل قدیمی", "در برخی تجهیزات قدیمی فعال است"),
            ("VFD-VL", "تخصصی آسانسور", "سری مرتبط با کاربردهای آسانسوری"),
        ],
        "models_en": [
            ("VFD-EL", "Light-duty general use; small motors", "Economical for basic applications"),
            ("VFD-MS300", "Advanced general-purpose vector control", "Modern, widely used family"),
            ("VFD-M", "General purpose, older generation", "Common in legacy equipment"),
            ("VFD-C2000", "Heavy-duty, high torque", "For demanding industrial environments"),
            ("VFD-B", "Heavy-duty, older generation", "Still found in some older equipment"),
            ("VFD-VL", "Elevator-specific applications", "Elevator drive family"),
        ],
        "faults_fa": [
            ("VFD-EL", "OC · اضافه‌جریان", "اتصال کوتاه خروجی یا خرابی IGBT", "بررسی موتور و کابل و تست بخش قدرت", "delta-inverter-oc-overcurrent"),
            ("VFD-MS300", "OV · اضافه‌ولتاژ", "انرژی برگشتی موتور هنگام توقف سریع", "بررسی مقاومت ترمز و زمان توقف", "delta-inverter-ov-overvoltage-error-analysis"),
            ("VFD-M", "LV · افت ولتاژ", "نوسان شبکه یا افت ظرفیت خازن‌های لینک DC", "اندازه‌گیری ورودی و ارزیابی خازن‌ها؛ کد مقالهٔ موجود متفاوت است", None),
            ("VFD-C2000", "OH / OH1 · دمای بالا", "فن، هیت‌سینک یا سنسور دما", "بررسی تهویه و سرویس خنک‌کننده؛ راهنمای OH در دسترس است", "delta-inverter-oh-overheat"),
            ("VFD-B", "OL · اضافه‌بار درایو", "تنظیم نادرست موتور یا گشتاور بالا", "بررسی جریان نامی موتور و تنظیمات حفاظت", "delta-inverter-ol-overload"),
            ("VFD-B", "OL1 · اضافه‌بار موتور", "بار مکانیکی یا جریان موتور بالاتر از حد", "بررسی بار و اطلاعات پلاک موتور", "delta-inverter-ol1-motor-overload"),
            ("VFD-VL", "GF · اتصال زمین", "نشتی از سیم‌پیچ موتور یا کابل خروجی", "بررسی ایمن عایق موتور و کابل", "delta-inverter-gf-ground-fault"),
        ],
        "faults_en": [
            ("VFD-EL", "OC · Overcurrent", "Output short circuit or IGBT fault", "Check motor, cable and power stage", "delta-inverter-oc-overcurrent"),
            ("VFD-MS300", "OV · Overvoltage", "Regenerative energy during rapid stopping", "Check braking resistor and deceleration time", "delta-inverter-ov-overvoltage-error-analysis"),
            ("VFD-M", "LV · Low voltage", "Supply fluctuation or aged DC-link capacitors", "Measure input and assess capacitors; the available article covers a different code", None),
            ("VFD-C2000", "OH / OH1 · Overheat", "Fan, heatsink or temperature sensor issue", "Check ventilation and cooling; OH guide available", "delta-inverter-oh-overheat"),
            ("VFD-B", "OL · Drive overload", "Incorrect motor settings or high torque demand", "Check motor rated current and protection settings", "delta-inverter-ol-overload"),
            ("VFD-B", "OL1 · Motor overload", "Mechanical load or motor current above limit", "Check load and motor nameplate data", "delta-inverter-ol1-motor-overload"),
            ("VFD-VL", "GF · Ground fault", "Leakage from motor winding or output cable", "Safely assess motor and cable insulation", "delta-inverter-gf-ground-fault"),
        ],
    },
    "schneider": {
        "intro_fa": "خانوادهٔ Altivar مدل‌های متنوعی برای کاربردهای عمومی، سنگین و آسانسوری دارد. این جدول، نمونهٔ مدل‌ها و خطاهای درج‌شده در فایل مرجع را کنار هم می‌آورد.",
        "intro_en": "Altivar includes general-purpose, heavy-duty and elevator applications. The tables pair example models with faults listed in the supplied reference.",
        "models_fa": [
            ("Altivar 12 (ATV12)", "ماشین‌آلات کوچک، فن و پمپ", "رایج در کاربردهای عمومی سبک"),
            ("Altivar 310 (ATV310)", "کاربری صنعتی عمومی", "اقتصادی و رایج در صنایع سبک و متوسط"),
            ("Altivar 312 (ATV312)", "کاربری صنعتی عمومی، نسل قدیمی‌تر", "هنوز در پروژه‌های قدیمی فعال است"),
            ("Altivar 71 (ATV71)", "کاربردهای سنگین", "در صنایع سنگین نیز استفاده شده"),
            ("Altivar 320 (ATV320)", "کنترل صنعتی پیشرفته", "کنترل گشتاور و سرعت"),
            ("Altivar 71 / 31", "آسانسور و بالابر در مدل‌های خاص", "محدودهٔ مدل دقیق باید بررسی شود"),
        ],
        "models_en": [
            ("Altivar 12 (ATV12)", "Small machines, fans and pumps", "Common in light-duty applications"),
            ("Altivar 310 (ATV310)", "General industrial use", "Economical for light and medium industry"),
            ("Altivar 312 (ATV312)", "General industrial, older generation", "Still active in legacy installations"),
            ("Altivar 71 (ATV71)", "Heavy-duty applications", "Also found in heavy industry"),
            ("Altivar 320 (ATV320)", "Advanced industrial control", "Torque and speed control"),
            ("Altivar 71 / 31", "Elevators and lifts in specific models", "Confirm the exact model range"),
        ],
        "faults_fa": [
            ("ATV12", "OCF · اضافه‌جریان", "اتصال کوتاه خروجی یا شتاب‌گیری سریع", "بررسی موتور و کابل و تست IGBT", "schneider-drive-ocf"),
            ("ATV310", "OSF · اضافه‌ولتاژ شبکه", "نوسان شبکه یا انرژی برگشتی موتور", "بررسی شبکه و تنظیمات ترمز", "schneider-drive-osf"),
            ("ATV312", "USF · افت ولتاژ", "قطع فاز ورودی یا افت شدید ولتاژ", "بررسی تغذیه، کنتاکتورها و خازن DC", "schneider-drive-usf"),
            ("ATV71", "OHF · دمای بالای درایو", "فن معیوب، محیط گرم یا اضافه‌بار", "بررسی فن، هیت‌سینک و شرایط نصب", "schneider-drive-ohf"),
            ("ATV320", "OLF · اضافه‌بار موتور", "تنظیم نامناسب جریان نامی موتور", "بررسی و تطبیق پارامتر ITH با پلاک موتور", "schneider-drive-olf"),
            ("ATV71 / 31 آسانسوری", "InF · خطای داخلی", "احتمال ایراد برد یا مدار منطقی", "ارزیابی تخصصی برد؛ مقالهٔ اختصاصی موجود نیست", None),
        ],
        "faults_en": [
            ("ATV12", "OCF · Overcurrent", "Output short circuit or fast acceleration", "Check motor and cable; test IGBTs", "schneider-drive-ocf"),
            ("ATV310", "OSF · Mains overvoltage", "Grid fluctuation or regenerative motor energy", "Check supply and braking settings", "schneider-drive-osf"),
            ("ATV312", "USF · Undervoltage", "Input phase loss or severe voltage drop", "Check supply, contactors and DC capacitors", "schneider-drive-usf"),
            ("ATV71", "OHF · Drive overheat", "Fan fault, high ambient temperature or overload", "Check fan, heatsink and installation conditions", "schneider-drive-ohf"),
            ("ATV320", "OLF · Motor overload", "Incorrect motor rated-current setting", "Compare ITH with the motor nameplate", "schneider-drive-olf"),
            ("ATV71 / 31 elevator", "InF · Internal fault", "Possible board or logic-circuit fault", "Specialist board diagnosis; no dedicated article yet", None),
        ],
    },
    "inovance": {
        "intro_fa": "در این صفحه، مدل‌های Goodrive ثبت‌شده برای Inovance در فایل مرجع، از GD10 و GD20 تا GD200A، GD350 و مدل‌های آسانسوری و پمپ خورشیدی، کنار هم آمده‌اند. کدهایی مانند OC1، OC2 و OC3 به وضعیت کاری متفاوت اشاره دارند؛ بنابراین ثبت مدل دقیق، کاربرد و زمان بروز خطا برای عیب‌یابی ضروری است.",
        "intro_en": "This Inovance page groups the Goodrive models listed for it in the supplied reference, from GD10 and GD20 to GD200A, GD350, elevator and solar-pump models. Codes such as OC1, OC2 and OC3 refer to different operating conditions, so the exact model, application and fault timing matter.",
        "models_fa": [
            ("Goodrive 10 (GD10)", "عمومی و سبک؛ فن، پمپ و بسته‌بندی", "۰٫۲ تا ۲٫۲ کیلووات؛ فشرده و اقتصادی"),
            ("Goodrive 20 (GD20)", "عمومی پیشرفته و کنترل برداری", "۰٫۴ تا ۱۱۰ کیلووات؛ پرکاربرد صنعتی"),
            ("Goodrive 200A (GD200A)", "عمومی سنگین", "۰٫۷۵ تا ۵۰۰ کیلووات؛ اضافه‌بارپذیری بالا"),
            ("Goodrive 350 (GD350)", "اتوماسیون و کنترل دقیق", "۱٫۵ تا ۶۳۰ کیلووات؛ قابلیت کارت‌های شبکه و انکودر"),
            ("GD300-01", "کمپرسور اسکرو", "کنترل حلقه‌بستهٔ فشار و دما"),
            ("CHV180 / GD300-19", "آسانسور و بالابر", "کنترل ترمز و پیش‌گشتاور"),
            ("GD100-PV / BPD", "پمپ خورشیدی", "MPPT و کار مستقیم با پنل"),
            ("CHE100 / CHF100A", "نسل قدیمی", "هنوز در برخی کارخانجات فعال است"),
        ],
        "models_en": [
            ("Goodrive 10 (GD10)", "Light-duty fans, pumps and packaging", "0.2–2.2 kW; compact and economical"),
            ("Goodrive 20 (GD20)", "Advanced general purpose, vector control", "0.4–110 kW; widely used in industry"),
            ("Goodrive 200A (GD200A)", "Heavy-duty general purpose", "0.75–500 kW; high overload capacity"),
            ("Goodrive 350 (GD350)", "Advanced automation and precise control", "1.5–630 kW; network and encoder options"),
            ("GD300-01", "Screw compressors", "Closed-loop pressure and temperature control"),
            ("CHV180 / GD300-19", "Elevators and lifts", "Brake control and pre-torque features"),
            ("GD100-PV / BPD", "Solar water pumps", "MPPT and direct PV operation"),
            ("CHE100 / CHF100A", "Legacy models", "Still operating in some factories"),
        ],
        "faults_fa": [
            ("Goodrive 10", "OUT1 / OUT2 / OUT3 · حفاظت IGBT", "اتصال کوتاه یا خطای زمین در خروجی", "بررسی ایمن کابل و موتور؛ تست IGBT و گیت‌درایو در تعمیرگاه", None),
            ("Goodrive 20", "OC1 · اضافه‌جریان شتاب‌گیری", "شتاب‌گیری سریع یا بار اولیهٔ سنگین", "تنظیم زمان شتاب و پارامتر موتور؛ بررسی بار", ("invt-drive-overcurrent-oc", "راهنمای کلی OC")),
            ("Goodrive 200A", "OC2 · اضافه‌جریان کاهش سرعت", "کاهش سرعت سریع بدون دفع انرژی ترمز", "تنظیم زمان توقف و بررسی مقاومت ترمز", ("invt-drive-overcurrent-oc", "راهنمای کلی OC")),
            ("Goodrive 350", "OC3 · اضافه‌جریان سرعت ثابت", "تغییر ناگهانی بار یا مشکل کابل/ورودی", "بررسی بار، موتور و کابل خروجی", ("invt-drive-overcurrent-oc", "راهنمای کلی OC")),
            ("GD300-01", "OV1 / OV2 / OV3 · اضافه‌ولتاژ", "انرژی برگشتی موتور یا ولتاژ بالای شبکه", "بررسی ولتاژ ورودی و مدار ترمز", ("invt-drive-overvoltage-ov", "راهنمای کلی OV")),
            ("CHV180 / GD300-19", "UV · افت ولتاژ", "افت فاز ورودی یا نقص شارژ باس DC", "بررسی فیوزها، پل دیود، رلهٔ بای‌پس و خازن‌ها", "invt-drive-undervoltage-uv"),
            ("GD100-PV / BPD", "OL1 · اضافه‌بار موتور", "بار زیاد یا تنظیم نادرست جریان نامی", "تطبیق پارامتر موتور و بررسی بار مکانیکی", ("invt-drive-overload-ol", "راهنمای کلی OL")),
            ("CHE100 / CHF100A", "OL2 · اضافه‌بار درایو", "توان درایو کمتر از بار یا کار مداوم در حد بالا", "بررسی تناسب ظرفیت و تنظیمات کنترل", ("invt-drive-overload-ol", "راهنمای کلی OL")),
            ("مدل‌های وابسته", "OH1 / OH2 · دمای بالا", "هیت‌سینک، فن یا مسیر هوای مسدود", "بررسی فن و تهویه؛ سرویس فقط در حالت ایمن", "invt-drive-overheating-oh"),
            ("مدل‌های وابسته", "ETH1 / ETH2 · حفاظت حرارتی", "حفاظت حرارتی موتور/درایو بر اساس بار و سرعت", "بررسی جریان، بار و شرایط خنک‌کاری؛ مقالهٔ اختصاصی موجود نیست", None),
            ("مدل‌های وابسته", "EF · خطای خارجی", "فعال شدن ورودی خطای خارجی", "بررسی زنجیرهٔ فرمان و ترمینال‌های ورودی؛ مقالهٔ اختصاصی موجود نیست", None),
            ("مدل‌های وابسته", "CE · قطع ارتباط", "اختلال ارتباط Modbus/RS485", "بررسی کابل، شیلد و مقاومت انتهای خط", "invt-drive-communication-error"),
            ("مدل‌های وابسته", "SPI / SPO · قطع فاز", "قطعی فاز ورودی یا خروجی", "بررسی کابل، کنتاکتور و بالانس سیم‌پیچ", "invt-drive-phase-loss-pl"),
        ],
        "faults_en": [
            ("Goodrive 10", "OUT1 / OUT2 / OUT3 · IGBT protection", "Output short circuit or ground fault", "Safely check cable and motor; workshop IGBT/gate-driver test", None),
            ("Goodrive 20", "OC1 · Acceleration overcurrent", "Fast acceleration or heavy starting load", "Adjust ramp and motor data; check load", ("invt-drive-overcurrent-oc", "General OC guide")),
            ("Goodrive 200A", "OC2 · Deceleration overcurrent", "Fast deceleration without braking-energy handling", "Adjust stop time and inspect braking resistor", ("invt-drive-overcurrent-oc", "General OC guide")),
            ("Goodrive 350", "OC3 · Constant-speed overcurrent", "Sudden load change or cable/input issue", "Check load, motor and output cable", ("invt-drive-overcurrent-oc", "General OC guide")),
            ("GD300-01", "OV1 / OV2 / OV3 · Overvoltage", "Regenerative motor energy or high supply voltage", "Check input voltage and braking circuit", ("invt-drive-overvoltage-ov", "General OV guide")),
            ("CHV180 / GD300-19", "UV · Undervoltage", "Input phase drop or DC-bus charging fault", "Check fuses, rectifier, bypass relay and capacitors", "invt-drive-undervoltage-uv"),
            ("GD100-PV / BPD", "OL1 · Motor overload", "High load or incorrect rated-current setting", "Match motor parameters and inspect mechanical load", ("invt-drive-overload-ol", "General OL guide")),
            ("CHE100 / CHF100A", "OL2 · Inverter overload", "Drive undersized for load or prolonged high-current operation", "Check drive capacity and control settings", ("invt-drive-overload-ol", "General OL guide")),
            ("Model-dependent", "OH1 / OH2 · Overheat", "Heatsink, fan or blocked airflow", "Check fan and ventilation; service only when safely isolated", "invt-drive-overheating-oh"),
            ("Model-dependent", "ETH1 / ETH2 · Thermal protection", "Motor/drive thermal protection based on load and speed", "Check current, load and cooling; no dedicated article yet", None),
            ("Model-dependent", "EF · External fault", "External fault input has been activated", "Check command chain and input terminals; no dedicated article yet", None),
            ("Model-dependent", "CE · Communication loss", "Modbus/RS485 communication problem", "Check cable, shielding and termination", "invt-drive-communication-error"),
            ("Model-dependent", "SPI / SPO · Phase loss", "Input- or output-phase interruption", "Check wiring, contactor and motor-winding balance", "invt-drive-phase-loss-pl"),
        ],
    },
}


BRAND_INTRO_COPY = {
    "yaskawa": (
        "درایوهای یاسکاوا در خدمات ما برای کاربردهای صنعتی و آسانسوری بررسی می‌شوند. برای عیب‌یابی، مدل کامل و کد خطا کنار شرایط توقف یا حرکت ثبت می‌شود؛ سپس موتور، کابل و تنظیمات بررسی و در صورت نیاز برد قدرت و کنترل در تعمیرگاه ارزیابی می‌شود.",
        "Yaskawa drives in our service scope are used in industrial and elevator applications. Diagnosis starts with the full model, fault code and operating symptoms, then checks the motor, cabling and settings before assessing the power and control boards when needed.",
    ),
    "monarch": (
        "مونارک در این فهرست به درایوها و کنترلرهای مورد استفاده در آسانسور مربوط است. هنگام تعمیر، خود کد خطا به‌تنهایی کافی نیست؛ مدل کنترلر، نوع موتور و شرایط بروز توقف یا حرکت نامنظم هم بررسی می‌شود تا بخش درایو و ارتباط آن با سامانهٔ آسانسور درست ارزیابی شود.",
        "Monarch here refers to drives and controllers used in elevator systems. A fault code alone is not enough for diagnosis: the controller model, motor type and conditions around a stop or irregular movement are checked so the drive and its elevator-system connections can be assessed together.",
    ),
    "hpmont": (
        "درایوهای اچ‌پی‌مونت (HPMont) در فهرست این سایت برای تجهیزات آسانسوری قرار دارند. عیب‌یابی با شناسایی مدل و ثبت کد و زمان بروز خطا شروع می‌شود؛ سپس تنظیمات موتور، اتصالات فرمان و قدرت و عملکرد درایو در شرایط ایمن بررسی می‌شود.",
        "HPMont drives are listed here under elevator equipment. Diagnosis begins by identifying the model and recording the code and fault timing, then checks motor settings, control and power connections, and drive operation under safe test conditions.",
    ),
    "zilabeg": (
        "خدمات زیلابگ در این فهرست به تجهیزات محرکه و درایوهای آسانسوری مربوط است. برای پیدا کردن منشأ ایراد، رفتار موتور و حرکت کابین با کد ثبت‌شده مقایسه می‌شود و اتصالات، تنظیمات و بخش‌های قدرت و کنترل متناسب با مدل بررسی می‌شوند.",
        "Zilabeg service in this catalogue focuses on elevator drive equipment. To locate a fault, motor and car behavior is considered alongside the recorded code, while connections, settings and model-specific power and control sections are checked.",
    ),
    "delta": (
        "خانوادهٔ درایوهای دلتا از مدل‌های عمومی و فشرده تا سری‌های سنگین و آسانسوری را دربرمی‌گیرد؛ از جمله VFD-EL، MS300، C2000 و VFD-VL. چون کدهایی مانند LV، OV و OL ممکن است بین سری‌ها تفاوت داشته باشند، عیب‌یابی را با مدل دقیق آغاز می‌کنیم و سپس بار، موتور، کابل و مدار قدرت را بررسی می‌کنیم.",
        "Delta drive families range from compact general-purpose models to heavy-duty and elevator series, including VFD-EL, MS300, C2000 and VFD-VL. Since codes such as LV, OV and OL can vary by series, diagnosis starts with the exact model, then checks the load, motor, cabling and power stage.",
    ),
    "inovance": (
        "در این صفحه، مدل‌های Goodrive ثبت‌شده برای Inovance، از درایوهای عمومی و صنعتی تا مدل‌های آسانسوری و پمپ خورشیدی، معرفی می‌شوند. عیب‌یابی بر اساس مدل و کاربرد دستگاه انجام می‌شود؛ مشخصات موتور، تنظیمات، اتصالات و بخش‌های قدرت و کنترل متناسب با همان مدل بررسی می‌شوند.",
        "This page presents the Goodrive models listed for Inovance, from general-purpose and industrial drives to elevator and solar-pump models. Diagnosis depends on the exact model and application; technicians check motor data, settings, wiring and model-specific power and control sections.",
    ),
    "growatt": (
        "گرووات در این سایت در گروه اینورترهای خورشیدی قرار دارد. عیب‌یابی با ثبت مدل، کد خطا و شرایط تولید یا اتصال به شبکه شروع می‌شود؛ سپس ورودی پنل، خروجی AC، تنظیمات و بخش‌های حفاظتی متناسب با نوع دستگاه بررسی می‌شوند.",
        "Growatt is listed here for solar inverters. Diagnosis starts by recording the model, fault code and production or grid conditions, then checks the PV input, AC output, settings and protection circuits appropriate to the unit.",
    ),
    "siemens": (
        "زیمنس خانواده‌های SINAMICS و MICROMASTER را برای کاربردهای مختلف عرضه می‌کند. V20 برای کاربردهای عمومی، G120/G120C برای صنعت، S120 برای سروو و چندمحوره و MICROMASTER 420/440 در تجهیزات قدیمی‌تر دیده می‌شوند. چون کد خطا به سری وابسته است، عیب‌یابی با مدل کامل آغاز می‌شود و سپس موتور و مدارهای قدرت و کنترل متناسب با آن بررسی و تست می‌شوند.",
        "Siemens offers SINAMICS and MICROMASTER drive families for different applications. V20 is used for general applications, G120/G120C for industry, S120 for servo and multi-axis systems, and MICROMASTER 420/440 remain in older equipment. Since fault definitions depend on the series, diagnosis starts with the full model before checking the motor, power and control sections and testing the repair.",
    ),
    "schneider": (
        "خانوادهٔ Altivar اشنایدر مدل‌های عمومی ATV12 و ATV310/312، مدل‌های سنگین‌تر ATV71 و ATV320 و برخی پیکربندی‌های آسانسوری را شامل می‌شود. برای تفسیر درست کدهایی مانند OCF، OSF یا USF، ابتدا مدل دقیق و کاربرد آن مشخص می‌شود و سپس ورودی، موتور، تنظیمات و بخش قدرت بررسی می‌شوند.",
        "Schneider's Altivar family includes general-purpose ATV12 and ATV310/312, heavier ATV71 and ATV320 models, and some elevator configurations. To interpret codes such as OCF, OSF or USF correctly, diagnosis first confirms the exact model and application, then checks the supply, motor, settings and power stage.",
    ),
    "ls": (
        "درایوهای ال‌اس (LS) در فهرست خدمات برای کاربردهای آسانسوری آمده‌اند. در تعمیر، مدل و کد خطا با وضعیت حرکت، فرمان‌ها و داده‌های موتور تطبیق داده می‌شوند؛ سپس کابل‌کشی، تنظیمات و بخش‌های قدرت و کنترل بررسی می‌شوند تا ایراد بیرونی از خرابی خود درایو تفکیک شود.",
        "LS drives are included in our elevator-service list. Repair diagnosis compares the model and fault code with motion behavior, commands and motor data, then checks wiring, settings and the power and control sections to distinguish an external issue from an internal drive fault.",
    ),
    "fuji": (
        "درایوهای Fuji Electric در این فهرست برای کاربردهای آسانسوری پوشش داده شده‌اند. مدل دقیق، نوع موتور و شرایط بروز خطا مبنای بررسی است؛ بعد از کنترل اتصالات و پارامترها، مدارهای قدرت و کنترل و عملکرد درایو متناسب با همان کاربرد تست می‌شوند.",
        "Fuji Electric drives are covered here for elevator applications. The exact model, motor type and fault conditions guide diagnosis; after checking connections and parameters, the power and control circuits are assessed and the drive is tested for its intended application.",
    ),
    "danfoss": (
        "درایوهای دانفوس در این سایت برای کاربردهای آسانسوری معرفی شده‌اند. چون خانواده‌ها و پیکربندی‌های مختلف می‌توانند کدها و تنظیمات متفاوتی داشته باشند، بررسی با پلاک مدل و سابقهٔ خطا شروع می‌شود و سپس موتور، اتصالات، پارامترهای حرکتی و بردهای قدرت و کنترل ارزیابی می‌شوند.",
        "Danfoss drives are listed here for elevator applications. Different families and configurations may use different codes and settings, so diagnosis starts with the model plate and fault history, then evaluates the motor, wiring, motion parameters and power and control boards.",
    ),
    "abb": (
        "درایوهای ABB (ای‌بی‌بی) در فهرست خدمات برای کاربردهای آسانسوری، صنعتی و خورشیدی پوشش داده شده‌اند. مسیر تعمیر با تعیین سری و کاربرد دستگاه مشخص می‌شود؛ سپس کد خطا، شرایط ورودی و خروجی و اجزای مرتبط با همان کاربرد بررسی می‌شوند تا تست نهایی نیز با نوع درایو هماهنگ باشد.",
        "ABB is covered here across elevator, industrial and solar-drive applications. The repair path depends on the drive family and use case; technicians check the fault code, input/output conditions and relevant hardware, then test the unit for its intended application.",
    ),
    "sbt": (
        "درایوهای اس‌بی‌تی (SBT) در فهرست خدمات ما به کاربردهای آسانسوری مربوط‌اند. برای تعمیر یک مدل مشخص، شمارهٔ مدل و کد خطا اهمیت دارد؛ بررسی می‌تواند شامل فرمان حرکت، اتصالات موتور و ترمز، پارامترهای درایو و تست عملکرد پس از تعمیر باشد.",
        "SBT is listed here for elevator drives. The exact model number and fault code are essential when identifying or repairing a unit; checks may include motion commands, motor and brake connections, drive parameters and post-repair functional testing.",
    ),
    "kyuma": (
        "QMA در این سایت به‌عنوان برند درایو آسانسوری معرفی شده است. هنگام عیب‌یابی، مدل دقیق و کد نمایش‌داده‌شده همراه با علائم حرکت بررسی می‌شوند؛ سپس اتصالات، پارامترهای موتور و بخش‌های قدرت و کنترل متناسب با دستگاه ارزیابی و عملکرد آن تست می‌شود.",
        "QMA is listed here as an elevator-drive brand. Diagnosis uses the exact model and displayed code together with motion symptoms; connections, motor parameters and the unit's power and control sections are then assessed and function-tested.",
    ),
    "solarx": (
        "سولارکس در فهرست شما با خطاهای ورودی پنل، اتصال شبکه، خروجی AC و باتری پوشش داده شده است؛ پشتیبانی باتری فقط برای مدل‌هایی مطرح است که این قابلیت را دارند. برای عیب‌یابی، مدل، وضعیت شبکه و تابش، آرایش رشته‌های پنل و کد دقیق ثبت می‌شود؛ تست مدارهای DC/AC باید توسط تکنسین واجد صلاحیت انجام شود.",
        "Your SolarX material covers PV-input, grid, AC-output and battery faults; battery support applies only to models equipped for it. Diagnosis records the model, grid and irradiance conditions, PV string layout and exact code. DC/AC testing should be performed by a qualified technician.",
    ),
    "voltronic": (
        "ولت‌رونیک در فهرست خدمات برای سانورترها و اینورترهای خورشیدی قرار دارد. در مدل‌هایی که باتری و شارژر داخلی دارند، وضعیت باتری و تنظیمات شارژ هم در کنار ورودی پنل و خروجی AC بررسی می‌شود؛ نوع قابلیت‌ها به مدل دستگاه وابسته است.",
        "Voltronic is listed here for solar inverters and inverter-chargers. On models with a battery interface and built-in charger, battery condition and charging settings are checked alongside PV input and AC output; available functions depend on the exact model.",
    ),
    "sma": (
        "اینورترهای خورشیدی SMA (اس‌ام‌ای) در این سایت پوشش داده شده‌اند. برای تشخیص خطای تولید یا اتصال شبکه، کد دستگاه، شرایط تابش، داده‌های ورودی DC و وضعیت خروجی AC کنار هم بررسی می‌شوند؛ ساختار و قابلیت‌های حفاظتی با خانوادهٔ محصول فرق دارد.",
        "SMA is covered here for solar inverters. To diagnose production or grid-connection faults, technicians consider the code, irradiance, DC input data and AC output together; architecture and protection features vary by product family.",
    ),
    "fronius": (
        "در این صفحه، خدمات فرونیوس به اینورترهای خورشیدی محدود است. عیب‌یابی بر اساس مدل و کد ثبت‌شده انجام می‌شود و می‌تواند ورودی پنل، اتصال شبکه، شرایط دمایی و مدارهای قدرت را دربر بگیرد؛ آزمون تعمیر نیز با مشخصات همان دستگاه تطبیق داده می‌شود.",
        "This Fronius page focuses on solar inverters. Diagnosis uses the model and recorded code and may cover PV input, grid connection, temperature conditions and power circuits; repair testing is matched to the unit's specifications.",
    ),
    "huawei": (
        "هوآوی در این فهرست برای اینورترهای خورشیدی معرفی شده است. عیب‌یابی به مدل و آرایش سامانه وابسته است و می‌تواند بررسی ورودی DC، ارتباط با سامانهٔ پایش، اتصال شبکه و بخش‌های قدرت را دربر بگیرد؛ از روی نام برند به‌تنهایی نمی‌توان علت خطا را تعیین کرد.",
        "Huawei is listed here for solar inverters. Diagnosis depends on model and system configuration and may involve DC input, monitoring communications, grid connection and power circuits; the brand name alone does not determine a fault cause.",
    ),
    "sungrow": (
        "اینورترهای خورشیدی Sungrow (سانگرو) و تجهیزات مرتبط نیروگاه در فهرست خدمات ما قرار دارند. هنگام افت تولید یا قطع اتصال، داده‌های ورودی پنل، شرایط شبکه، دما و کد ثبت‌شده با مدل دستگاه تطبیق داده می‌شوند؛ سپس حفاظت‌ها و مدارهای قدرت ارزیابی می‌شوند.",
        "Sungrow is covered for solar inverters and solar-plant equipment. For low production or disconnection, PV input data, grid conditions, temperature and the recorded code are checked against the model before protection and power circuits are assessed.",
    ),
    "goodwe": (
        "اینورترهای خورشیدی GoodWe (گودوی) در این سایت پوشش داده شده‌اند. بسته به مدل، دستگاه ممکن است با شبکه یا باتری کار کند؛ بنابراین پیش از بررسی خطا باید نوع سیستم و تجهیزات متصل مشخص شود. عیب‌یابی بر ورودی PV، خروجی AC، ارتباطات و حفاظت‌های همان مدل متمرکز است.",
        "GoodWe is listed here for solar inverters. Depending on the model, a unit may operate with the grid or a battery, so the system configuration and connected equipment should be identified first. Diagnosis then focuses on that model's PV input, AC output, communications and protections.",
    ),
    "solis": (
        "اینورترهای خورشیدی Solis (سولیس) در فهرست خدمات ما قرار دارند. بررسی افت تولید، خطای شبکه یا عملکرد ناپایدار باید با توجه به مدل و آرایش پنل‌ها انجام شود؛ ورودی‌های PV، خروجی AC و بخش پایش و حفاظت با اطلاعات ثبت‌شده تطبیق داده می‌شوند.",
        "Solis is listed here for solar inverters. Low production, grid faults or unstable operation should be assessed against the model and PV-array configuration; PV inputs, AC output, monitoring and protection are compared with recorded data.",
    ),
    "sofar": (
        "اینورترهای خورشیدی Sofar (سوفار) در فهرست خدمات ما هستند. چون طراحی و قابلیت‌های محصول با سری و مدل فرق می‌کند، عیب‌یابی با مدل دقیق و کد خطا شروع می‌شود و سپس رشته‌های PV، برق شبکه، تنظیمات و مدارهای مرتبط بررسی می‌شوند.",
        "Sofar is listed here for solar inverters. Product design and functions vary by series, so diagnosis starts with the exact model and fault code before checking PV strings, grid supply, settings and related circuits.",
    ),
    "must": (
        "تجهیزات خورشیدی و سانورترهای MUST (ماست) در فهرست خدمات ما قرار دارند. در مدل‌های باتری‌دار، سلامت باتری و تنظیم شارژ نیز اهمیت دارد؛ در مدل‌های دیگر، بررسی بر ورودی پنل و خروجی دستگاه متمرکز می‌شود. ابتدا باید پیکربندی واقعی با مدل و منوال تطبیق داده شود.",
        "MUST is covered here for solar equipment and inverter-chargers. Battery condition and charge settings matter on battery-equipped models; other units may focus on PV input and inverter output. First confirm the actual configuration against the model and manual.",
    ),
}

BRAND_INTRO_DETAILS = {
    "yaskawa": (
        "در آسانسور، هماهنگی درایو با موتور، فیدبک و ترمز اهمیت دارد؛ در کاربرد صنعتی، بار و زمان‌های شتاب و توقف هم بررسی می‌شوند. نتیجهٔ تعمیر با آزمون متناسب با همان کاربرد ارزیابی می‌شود.",
        "For elevators, drive, motor, feedback and brake coordination matters; industrial cases also call for checking load and acceleration/deceleration settings. The repair is tested for the intended application.",
    ),
    "monarch": (
        "اگر خطا هم‌زمان با توقف، تراز نشدن یا حرکت نامنظم کابین ظاهر شود، اطلاعات کنترلر و درایو باید با هم بررسی شوند. تعمیر قطعه بدون توجه به ارتباط آن با سامانهٔ آسانسور ممکن است علت اصلی را برطرف نکند.",
        "If a fault coincides with stopping, leveling or irregular car movement, controller and drive information should be reviewed together. Repairing a component without considering its elevator-system connections may leave the root cause unresolved.",
    ),
    "hpmont": (
        "در کاربرد آسانسوری، زمان بروز خطا نسبت به شروع حرکت و عملکرد ترمز سرنخ مهمی است. تنظیمات و اتصالات باید با مدل نصب‌شده تطبیق داده شوند؛ مقادیر یک مدل را نباید بدون بررسی به مدل دیگر منتقل کرد.",
        "In elevator applications, fault timing around startup and brake operation can provide useful clues. Settings and connections must be matched to the installed model; values should not be copied between models without verification.",
    ),
    "zilabeg": (
        "ثبت این‌که ایراد هنگام استارت، حرکت یا توقف رخ می‌دهد به تفکیک مشکل درایو از موتور و سامانهٔ آسانسور کمک می‌کند. پس از تعمیر، حرکت و توقف باید در شرایط کنترل‌شده بررسی شوند.",
        "Recording whether a fault occurs at startup, during travel or while stopping helps distinguish a drive issue from motor or elevator-system problems. Motion and stopping should be checked under controlled conditions after repair.",
    ),
    "delta": (
        "برای نمونه، اضافه‌جریان هنگام شتاب‌گیری با اضافه‌ولتاژ هنگام کاهش سرعت علت و مسیر بررسی یکسانی ندارد. کد، مدل و لحظهٔ بروز خطا را با هم ثبت کنید؛ لینک جدول فقط به مقاله‌ای می‌رود که با همان خانوادهٔ خطا مرتبط است.",
        "For example, acceleration overcurrent and deceleration overvoltage have different likely causes and diagnostic paths. Record the code, model and timing together; table links are provided only where a relevant fault guide exists.",
    ),
    "inovance": (
        "کدهایی مانند OC1، OC2 و OC3 به زمان رخداد—شتاب‌گیری، کاهش سرعت یا سرعت ثابت—وابسته‌اند. مشخصات مدل و منوال مرجع نهایی‌اند؛ پس از بررسی بار و تنظیمات، بخش قدرت و کنترل فقط در صورت نیاز و توسط تعمیرکار واجد صلاحیت ارزیابی می‌شود.",
        "Codes such as OC1, OC2 and OC3 depend on timing—acceleration, deceleration or steady speed. The exact model manual is authoritative; after checking load and settings, power and control hardware should be assessed only when indicated and by a qualified repairer.",
    ),
    "growatt": (
        "قابلیت باتری و نوع اتصال شبکه در همهٔ مدل‌ها یکسان نیست؛ پیش از بررسی، نوع دستگاه و پیکربندی واقعی سامانه مشخص می‌شود. داده‌های خطا و شرایط تولید به تشخیص تفاوت میان مسئلهٔ پنل، شبکه و خود اینورتر کمک می‌کنند.",
        "Battery functions and grid configurations are not the same across all models, so the actual unit and system setup should be identified first. Fault logs and production conditions help distinguish PV-side, grid-side and inverter issues.",
    ),
    "siemens": (
        "در یک سری، یک کد ممکن است به بخش متفاوتی نسبت به سری دیگر اشاره کند؛ بنابراین معنی کد باید با دفترچهٔ همان خانواده تطبیق داده شود. لینک‌های این صفحه فقط به راهنمای خطاهای موجود وصل شده‌اند و کدهای بدون مقاله به‌عنوان لینک حدس زده نشده‌اند.",
        "The same code can refer to different conditions across drive families, so its meaning must be checked against the manual for that series. Links on this page lead only to existing fault guides; no links are guessed for codes without an article.",
    ),
    "schneider": (
        "درایوهای Altivar را باید با کد کامل ATV و نسخهٔ دستگاه شناسایی کرد؛ تشابه ظاهری کدها به معنی یکسان بودن روند تعمیر نیست. خطای داخلی یا قدرت، اگر در جدول مقالهٔ اختصاصی ندارد، برای بررسی تخصصی به تعمیرگاه ارجاع می‌شود.",
        "Altivar units should be identified by their full ATV model and revision; similar-looking codes do not guarantee the same repair procedure. Internal or power faults without a dedicated guide require specialist workshop assessment.",
    ),
    "ls": (
        "در عیب‌یابی آسانسوری، زمان بروز خطا، وضعیت حرکت و فرمان ترمز در کنار کد ثبت می‌شوند. به این ترتیب می‌توان بررسی موتور و کابل را از تنظیمات یا مدارهای داخلی درایو جدا کرد.",
        "For elevator diagnosis, record fault timing, motion behavior and brake commands alongside the code. This helps separate motor and cable checks from drive settings or internal-circuit faults.",
    ),
    "fuji": (
        "کد خطای ثبت‌شده باید همراه با شمارهٔ مدل و شرایط بار بررسی شود، چون حفاظت‌ها بین نسل‌ها تفاوت دارند. در صورت سالم بودن موتور و کابل، بردهای کنترل و قدرت و عملکرد درایو در تعمیرگاه ارزیابی می‌شوند.",
        "Record the fault code with the model number and load conditions because protection behavior varies between generations. If the motor and cable are sound, the control and power boards and drive operation can be assessed in the workshop.",
    ),
    "danfoss": (
        "در کاربرد آسانسوری، رفتار خطا هنگام شتاب، حرکت یکنواخت و توقف می‌تواند مسیر عیب‌یابی را تغییر دهد. پارامترها و قطعات وابسته به ترمز فقط با توجه به مدل و نقشهٔ همان نصب بررسی می‌شوند.",
        "In elevator use, fault behavior during acceleration, steady travel and stopping can change the diagnostic path. Parameters and brake-related components should be checked against the exact model and installation drawings.",
    ),
    "abb": (
        "درایوهای این برند در چند نوع کاربرد این سایت دیده می‌شوند، اما روش بررسی هرکدام یکی نیست. مشخص کردن این‌که دستگاه آسانسوری، صنعتی یا خورشیدی است، کمک می‌کند عیب‌یابی از بخش درست—موتور و بار، ورودی/خروجی یا سمت PV—شروع شود.",
        "This brand appears in several application areas on our site, but their diagnostic paths differ. Identifying whether the unit is elevator, industrial or solar helps start with the right area: motor/load, AC input/output or the PV side.",
    ),
    "sbt": (
        "برای جلوگیری از تعویض یا تنظیم اشتباه، اطلاعات پلاک درایو و مدل کنترلر آسانسور هنگام پذیرش ثبت می‌شود. ارزیابی نهایی شامل بررسی ایمن مدارها و آزمون عملکرد در محدودهٔ مناسب دستگاه است.",
        "To avoid incorrect replacement or settings, the drive nameplate and elevator-controller model are recorded at intake. Final assessment includes safe circuit checks and an operational test appropriate to the equipment.",
    ),
    "kyuma": (
        "نام مدل و سامانهٔ کنترلی متصل، مبنای انتخاب روش بررسی QMA است. کدها و تنظیمات باید از مستندات همان دستگاه گرفته شوند و پس از تعمیر، هماهنگی درایو با موتور و فرمان‌های آسانسور بررسی شود.",
        "The QMA model and connected control system determine the diagnostic approach. Codes and settings should come from the unit's documentation, and drive coordination with the motor and elevator commands should be checked after repair.",
    ),
    "solarx": (
        "خطاهای PV، شبکه و باتری مسیرهای جداگانه دارند؛ وجود قابلیت باتری را باید از مدل و نقشهٔ نصب تأیید کرد. مدارهای خورشیدی DC ممکن است در روشنایی روز برق‌دار بمانند، بنابراین بازرسی و اندازه‌گیری فقط باید توسط فرد واجد صلاحیت انجام شود.",
        "PV, grid and battery faults have different diagnostic paths; battery capability should be confirmed from the model and installation design. Solar DC circuits can remain energized in daylight, so inspection and measurement belong to qualified personnel.",
    ),
    "voltronic": (
        "در مدل‌های دارای شارژر و ورودی باتری، باید تنظیم ولتاژ شارژ با شیمی و مشخصات باتری سازگار باشد؛ این قابلیت را نمی‌توان به همهٔ محصولات تعمیم داد. ثبت مدل و نوع باتری پیش از عیب‌یابی از تغییر تنظیمات نامتناسب جلوگیری می‌کند.",
        "On models with a charger and battery input, charging voltage must match the battery chemistry and specifications; this should not be generalized to every product. Recording the model and battery type helps avoid unsuitable setting changes.",
    ),
    "sma": (
        "برای خطاهای تولید، ورودی DC و شرایط رشته‌های پنل در کنار اتصال و کیفیت شبکه بررسی می‌شوند. حدود حفاظتی و روش تشخیص به خانوادهٔ اینورتر بستگی دارد، پس مدل دقیق و گزارش خطا همراه دستگاه لازم است.",
        "For production faults, DC input and PV-string conditions are considered alongside grid connection and quality. Protection limits and diagnosis vary by inverter family, so provide the exact model and fault report.",
    ),
    "fronius": (
        "برای اینورتر خورشیدی فرونیوس، شرایط تابش، آرایش رشته‌های پنل، اتصال شبکه و دمای کار ثبت می‌شوند. این داده‌ها کمک می‌کنند ایرادهای نصب و شبکه از نقص احتمالی داخل اینورتر تفکیک شوند و تست تعمیر با مشخصات همان مدل هماهنگ باشد.",
        "For a Fronius solar inverter, record irradiance, PV-string layout, grid connection and operating temperature. These details help distinguish installation or grid issues from a possible internal inverter fault and ensure repair testing matches the model.",
    ),
    "huawei": (
        "پیش از عیب‌یابی، مدل اینورتر، آرایش رشته‌های پنل و وضعیت سامانهٔ پایش ثبت می‌شود. اگر نشانه‌ها از سمت شبکه یا نصب باشند، تعمیرکار ابتدا همان عوامل بیرونی را از نقص احتمالی مدار داخلی تفکیک می‌کند.",
        "Before diagnosis, record the inverter model, PV-string layout and monitoring status. If symptoms point to the grid or installation, the technician separates those external causes from a possible internal-circuit fault.",
    ),
    "sungrow": (
        "تغییرات تابش، دمای محیط و وضعیت شبکه می‌توانند بر تولید سامانه اثر بگذارند، پس کد خطا به‌تنهایی برای تشخیص کافی نیست. گزارش تولید و مدل اینورتر کنار هم بررسی می‌شوند و سپس ورودی PV، خروجی AC و حفاظت‌های مرتبط تست می‌شوند.",
        "Irradiance, ambient temperature and grid conditions can affect production, so a fault code alone is not enough. Production records and the inverter model are reviewed together before checking the PV input, AC output and relevant protections.",
    ),
    "goodwe": (
        "در مدل‌های هیبریدی، باتری و ارتباط BMS نیز در مسیر عیب‌یابی قرار می‌گیرند؛ در مدل‌های دیگر این موارد کاربرد ندارند. به همین دلیل نوع سیستم، تجهیزات متصل و کد ثبت‌شده باید پیش از بررسی مشخص شوند.",
        "On hybrid models, the battery and BMS communication are part of the diagnostic path; these checks do not apply to every unit. Identify the system type, connected equipment and recorded code before troubleshooting.",
    ),
    "solis": (
        "در خطاهای متناوب، زمان رخداد و شرایط تابش یا شبکه ثبت می‌شوند تا مشکل نصب از ایراد خود دستگاه تفکیک شود. بررسی آرایش پنل‌ها و ولتاژهای DC باید در محدودهٔ مجاز مدل انجام گیرد.",
        "For intermittent faults, record timing and irradiance or grid conditions to distinguish installation issues from inverter faults. PV layout and DC voltage checks must stay within the model's ratings.",
    ),
    "sofar": (
        "اگر خطا با افت تولید همراه است، داده‌های رشته‌های PV و شرایط شروع به کار دستگاه اهمیت دارند؛ اگر هنگام اتصال شبکه رخ می‌دهد، ولتاژ و فرکانس شبکه هم بررسی می‌شوند. این دو مسیر نباید بدون توجه به مدل با یکدیگر اشتباه گرفته شوند.",
        "When a fault accompanies low production, PV-string data and startup conditions matter; if it occurs during grid connection, grid voltage and frequency should also be checked. These paths should not be conflated without considering the model.",
    ),
    "must": (
        "در دستگاه‌های متصل به باتری، ولتاژ و تنظیم شارژ باید با مشخصات باتری هماهنگ باشد؛ در کاربری پمپ خورشیدی، شرایط آرایه و بار موتور نیز اهمیت پیدا می‌کند. قابلیت واقعی هر دستگاه باید از روی مدل و منوال تأیید شود.",
        "For battery-connected units, voltage and charging settings must match the battery specifications; solar-pump applications also depend on PV-array and motor-load conditions. Confirm each unit's actual functions from its model and manual.",
    ),
}


for _brand in BRANDS:
    _copy = BRAND_INTRO_COPY[_brand["slug"]]
    _details = BRAND_INTRO_DETAILS[_brand["slug"]]
    _full_copy = (f"{_copy[0]}\n\n{_details[0]}", f"{_copy[1]}\n\n{_details[1]}")
    _guide = BRAND_PAGE_GUIDES.get(_brand["slug"])
    if _guide:
        _guide["intro_fa"], _guide["intro_en"] = _full_copy
    else:
        _brand["content_fa"] = "".join(
            f"<p>{html.escape(paragraph)}</p>" for paragraph in _full_copy[0].split("\n\n")
        )
        _brand["content_en"] = "".join(
            f"<p>{html.escape(paragraph)}</p>" for paragraph in _full_copy[1].split("\n\n")
        )


def _brand_reference_table(headers, rows, *, errors=False, related_label="مقالهٔ مرتبط"):
    head = "".join(f"<th scope=\"col\">{html.escape(value)}</th>" for value in headers)
    body = []
    for row in rows:
        values = list(row)
        link = values[-1] if errors else None
        cells = values[:-1] if errors else values
        rendered = []
        for index, value in enumerate(cells):
            text = html.escape(value)
            if errors and index == 1 and link:
                if isinstance(link, tuple):
                    slug, label = link
                    text += f" <a href=\"../articles/{html.escape(slug, quote=True)}\">({html.escape(label)})</a>"
                else:
                    text += f" <a href=\"../articles/{html.escape(link, quote=True)}\">({html.escape(related_label)})</a>"
            rendered.append(f"<td>{text}</td>")
        body.append("<tr>" + "".join(rendered) + "</tr>")
    return "<table><thead><tr>" + head + "</tr></thead><tbody>" + "".join(body) + "</tbody></table>"


for _brand in BRANDS:
    _guide = BRAND_PAGE_GUIDES.get(_brand["slug"])
    if not _guide:
        continue
    _brand["content_fa"] = (
        "".join(f"<p>{html.escape(paragraph)}</p>"
                for paragraph in _guide["intro_fa"].split("\n\n"))
        + "<h2>مدل‌های رایج و کاربردها</h2>"
        + _brand_reference_table(("سری / مدل", "کاربرد اصلی", "ویژگی و وضعیت بازار"), _guide["models_fa"])
        + "<h2>کدهای خطا و محور عیب‌یابی</h2>"
        + _brand_reference_table(("مدل مرتبط", "کد و عنوان خطا", "علت محتمل", "محور بررسی و تعمیر"), _guide["faults_fa"], errors=True, related_label="مقالهٔ مرتبط")
        + "<p><strong>یادآوری:</strong> معنی کد و حدود حفاظتی بین مدل‌ها و نسخه‌ها فرق می‌کند. علت‌ها محتمل‌اند؛ منوال همان دستگاه مرجع نهایی است و اندازه‌گیری داخل درایو باید توسط تعمیرکار واجد صلاحیت انجام شود.</p>"
    )
    _brand["content_en"] = (
        "".join(f"<p>{html.escape(paragraph)}</p>"
                for paragraph in _guide["intro_en"].split("\n\n"))
        + "<h2>Common models and applications</h2>"
        + _brand_reference_table(("Series / model", "Main application", "Features and market note"), _guide["models_en"])
        + "<h2>Fault codes and diagnostic focus</h2>"
        + _brand_reference_table(("Related model", "Code and fault", "Possible cause", "Repair focus"), _guide["faults_en"], errors=True, related_label="Read guide")
        + "<p><strong>Note:</strong> Codes and protection limits vary by model and revision. Causes are possibilities; the exact manual is authoritative. Internal measurements should be performed only by a qualified repair technician.</p>"
    )
BRAND_ORDER = {slug: index for index, slug in enumerate((
    "siemens", "delta", "yaskawa", "ls", "fuji", "danfoss", "abb", "inovance", "sbt",
    "monarch", "kyuma", "hpmont", "zilabeg", "growatt", "solarx",
    "voltronic", "sma", "fronius", "huawei", "sungrow", "goodwe", "solis", "sofar", "must",
))}

ARTICLES = [    {
        "slug": "delta-inverter-ov-overvoltage-error-analysis",
        "title_fa": "تحلیل تخصصی خطای OV (Overvoltage) در اینورترهای دلتا؛ چرا درایو شما «اضافه ولتاژ» می‌گیرد؟",
        "title_en": "Technical Analysis of OV (Overvoltage) Error in Delta Inverters",
        "excerpt_fa": "بررسی علل بروز خطای اضافه ولتاژ (OV) در اینورترهای دلتا، خرابی مقاومت ترمز، چاپر و نحوه رفع پایدار آن در مرکز تخصصی الکتروگلد.",
        "excerpt_en": "Comprehensive analysis of Delta inverter Overvoltage (OV) faults, braking resistor issues, DC bus capacitor failures, and professional repairs.",
        "body_fa": """
            <p>خطای <strong>OV (Overvoltage)</strong> در اینورترهای دلتا یکی از مواردی است که اگر به درستی ریشه‌یابی نشود، می‌تواند باعث آسیب‌های جدی به درایو و حتی سوختن یونیت ترمز (Braking Unit) شود. بسیاری از کاربران تصور می‌کنند این خطا فقط مربوط به «نوسانات برق شبکه» است، اما در واقعیت، ماجرا اغلب در داخل خود سیستمِ شما در جریان است.</p>

            <h2>چرا درایو شما دچار OV می‌شود؟</h2>
            <p>این خطا زمانی رخ می‌دهد که ولتاژ در لینک DC (خازن‌های داخل درایو) از حد مجاز فراتر می‌رود. این اتفاق معمولاً در دو حالتِ رایج رخ می‌دهد:</p>
            <ol>
                <li><strong>زمانِ توقف (Deceleration):</strong> وقتی موتور می‌خواهد سریع متوقف شود، اینرسی بار باعث می‌شود موتور مانند یک ژنراتور عمل کرده و انرژی را به سمت درایو برگرداند (Regeneration). اگر درایو نتواند این انرژی را تخلیه کند، ولتاژ بالا می‌رود و خطای OV رخ می‌دهد.</li>
                <li><strong>نوسانات شبکه (Input Voltage):</strong> اگر ولتاژ شبکه ورودی به طور ناگهانی افزایش یابد، درایو برای محافظت از خود، خروجی را قطع کرده و خطای OV می‌دهد.</li>
            </ol>

            <h2>آیا مقاومت ترمزِ شما سوخته است؟</h2>
            <p>یکی از بیشترین مراجعات ما به <strong>الکتروگلد</strong>، مربوط به درایوهایی است که به دلیل خرابی مقاومت ترمز یا سوختن «چاپر ترمز» (Braking Chopper) داخل دستگاه، دائم خطای OV می‌دهند.</p>
            
            <div style="background-color: #fff3cd; border-right: 4px solid #ffeeba; padding: 12px; margin: 15px 0;">
                <strong>هشدار فنی:</strong> اگر درایو شما در زمان توقف یا کاهش سرعت (Ramp Down) خطا می‌دهد، احتمالاً مقاومت ترمز شما در مدار نیست یا یونیت ترمز داخلی درایو دچار مشکل شده است. تکرارِ استارت در این شرایط، فشار شدیدی به خازن‌های باس DC وارد می‌کند و می‌تواند باعث باد کردن یا نشت آن‌ها شود.
            </div>

            <div style="background-color: #f8d7da; border-right: 4px solid #f5c6cb; padding: 12px; margin: 15px 0;">
                <strong>هشدار ایمنی الزامی:</strong> لینک DC در اینورترهای دلتا حتی پس از خاموش شدنِ نمایشگر، تا مدتی ولتاژ خطرناکی را در خود نگه می‌دارد. هرگز قبل از اندازه‌گیری دقیق ولتاژ DC با مولتی‌متر و اطمینان از تخلیه کامل، اقدام به باز کردن درایو یا تعویض مقاومت ترمز نکنید. خطر برق‌گرفتگی در این بخش بسیار بالاست.
            </div>

            <h2>الکتروگلد چگونه مشکل OV شما را حل می‌کند؟</h2>
            <p>ما در الکتروگلد فقط به «ریست کردن» اکتفا نمی‌کنیم. برای رفع دائمی خطای OV، فرآیند زیر را در کارگاه انجام می‌دهیم:</p>
            <ul>
                <li><strong>تست عملکرد چاپر ترمز:</strong> بررسی می‌کنیم که آیا درایو واقعاً فرمانِ تخلیه انرژی به مقاومت را صادر می‌کند یا خیر.</li>
                <li><strong>آنالیز سلامت خازن‌های باس DC:</strong> خازن‌های مستهلک نمی‌توانند نوسانات ولتاژ را جذب کنند و خودشان عامل بروز خطای کاذب OV می‌شوند.</li>
                <li><strong>تنظیم پارامترهای ترمز:</strong> گاهی اوقات مشکل با اصلاحِ «زمانِ کاهش سرعت» (Decel Time) یا تنظیماتِ «ولتاژِ سطحِ ترمز» حل می‌شود.</li>
            </ul>

            <h2>آیا درایو دلتای شما در زمان توقف موتور خطا می‌دهد؟</h2>
            <p>اجازه ندهید این مشکل به آسیب‌های گران‌قیمتِ سخت‌افزاری تبدیل شود. کارشناسان ما آماده‌اند تا با تست دقیقِ مسیر تخلیه انرژی، درایو شما را به پایداری بازگردانند.</p>
        """,
        "body_en": """
            <p>The <strong>OV (Overvoltage)</strong> fault in Delta inverters indicates that the DC bus voltage exceeds the safety threshold. This commonly happens during rapid deceleration or severe grid fluctuations.</p>
            <h2>Common Causes</h2>
            <ul>
                <li>Regenerative energy returning to the DC bus without adequate discharge.</li>
                <li>Defective or open-circuit braking resistor.</li>
                <li>Damaged internal braking chopper or aged DC bus capacitors.</li>
            </ul>
            <p>ElectroGold provides advanced diagnostics and repair services for industrial Delta inverters.</p>
        """,
        "author": "تیم فنی الکتروگلد",
        "image_query": "delta inverter repair industrial drive electronics",
        "services": ["industrial-inverter-repair"],
        "brands": ["delta"],
        "seo_title_fa": "رفع خطای OV در اینورتر دلتا | تعمیر تخصصی درایو الکتروگلد",
        "seo_title_en": "Delta Inverter OV Error Repair | ElectroGold",
        "seo_description_fa": "علت خطای OV یا اضافه ولتاژ در درایو دلتا چیست؟ عیب‌یابی مقاومت ترمز، چاپر و تست خازن لینک DC در کارگاه تخصصی الکتروگلد.",
        "seo_description_en": "Troubleshoot and fix Delta inverter Overvoltage (OV) faults with ElectroGold's specialized drive repair and diagnostics.",
    },
]
ARTICLES[0].update(DELTA_OV_ARTICLE_SOURCE)
ARTICLES.extend(DELTA_ERROR_ARTICLES)
ARTICLES.extend(SIEMENS_ERROR_ARTICLES)
ARTICLES.extend(YASKAWA_ERROR_ARTICLES)
ARTICLES.extend(SCHNEIDER_ERROR_ARTICLES)
ARTICLES.extend(GROWATT_ERROR_ARTICLES)
ARTICLES.extend(INVT_ERROR_ARTICLES)
ARTICLES.extend(SOLARX_ERROR_ARTICLES)
ARTICLES.extend(GENERAL_COMPARISON_ARTICLES)
ARTICLE_SLUGS = {record["slug"] for record in ARTICLES}
MANAGED_ARTICLE_SLUGS = {
    "delta-inverter-ov-overvoltage-error-analysis",
    "delta-inverter-gf-ground-fault",
    "delta-inverter-oc-overcurrent",
    "delta-inverter-oh-overheat",
    "delta-inverter-ol-overload",
    "delta-inverter-ol1-motor-overload",
    "delta-inverter-orp-output-phase-loss",
    "delta-inverter-phl-phase-loss",
    "delta-inverter-uv-undervoltage",
    "delta-inverter-ef-external-fault",
    "siemens-drive-f0001-instantaneous-overcurrent",
    "siemens-drive-f0002-dc-bus-overvoltage",
    "siemens-drive-f0003-undervoltage",
    "siemens-drive-f0004-heatsink-overtemperature",
    "siemens-drive-f0011-motor-overtemperature",
    "siemens-drive-f0012-model-specific-fault",
    "siemens-drive-f0015-f90-code-meaning",
    "siemens-drive-f0020-input-phase-loss",
    "siemens-drive-f0021-output-phase-loss",
    "siemens-drive-f0085-external-fault",
    "yaskawa-drive-ef-external-fault",
    "yaskawa-drive-gf-ground-fault",
    "yaskawa-drive-lf-output-phase-loss",
    "yaskawa-drive-oc-dc-bus-overvoltage",
    "yaskawa-drive-oh1-heatsink-overtemperature",
    "yaskawa-drive-ol1-motor-overload",
    "yaskawa-drive-ol2-inverter-overload",
    "yaskawa-drive-ov-dc-bus-overvoltage",
    "yaskawa-drive-pf-input-phase-loss",
    "yaskawa-drive-uv1-dc-bus-undervoltage",
    "schneider-drive-lff",
    "schneider-drive-ocf",
    "schneider-drive-ohf",
    "schneider-drive-olf",
    "schneider-drive-osf",
    "schneider-drive-phf",
    "schneider-drive-scf",
    "schneider-drive-ssf",
    "schneider-drive-thf",
    "schneider-drive-usf",
    "growatt-solar-ce",
    "growatt-solar-ef",
    "growatt-solar-errfault",
    "growatt-solar-oc",
    "growatt-solar-of",
    "growatt-solar-oh",
    "growatt-solar-ol",
    "growatt-solar-ov",
    "growatt-solar-ug",
    "growatt-solar-uv",
    "invt-drive-overcurrent-oc",
    "invt-drive-communication-error",
    "invt-drive-encoder-error",
    "invt-drive-ground-fault-gf",
    "invt-drive-internal-error",
    "invt-drive-overheating-oh",
    "invt-drive-overload-ol",
    "invt-drive-overvoltage-ov",
    "invt-drive-phase-loss-pl",
    "invt-drive-undervoltage-uv",
    "solarx-battery-fault",
    "solarx-communication-error",
    "solarx-earth-fault-ef",
    "solarx-grid-fault-ac-error",
    "solarx-isolation-fault-iso",
    "solarx-load-output-fault",
    "solarx-overcurrent-oc",
    "solarx-overheating-oh",
    "solarx-pv-overvoltage",
    "solarx-pv-undervoltage",
    "huawei-vs-sungrow-solar-inverter-comparison",
    "siemens-sinamics-vs-abb-acs-comparison",
    "delta-vs-invt-industrial-drive-comparison",
}
NON_ERROR_ARTICLE_SLUGS = {
    "elevator-inverter-fault-codes",
    "industrial-vfd-maintenance",
    "growatt-solar-errors",
    "monarch-controller-guide",
}

# The image service is best effort; these URLs keep every rendered card useful
# during an outage, and are supplied to find_images without entering a DB
# transaction.
for _record in SERVICES:
    _record["image_url"] = SERVICE_IMAGE_URLS[_record["slug"]]
    _record["focus_keyword_fa"] = _record["title_fa"]
    _record["focus_keyword_en"] = _record["title_en"].lower()
for _record in BRANDS:
    _record["image_url"] = BRAND_LOGO_PATHS[_record["slug"]]
SITE_SETTINGS = [
    {"language": "fa", "site_title": "الکتروگلد", "tagline": "خدمات اینورتر، درایو و خورشیدی",
     "hero_title": "خدمات اینورتر آسانسور، درایو صنعتی و خورشیدی",
     "hero_subtitle": "خدمات اینورتر آسانسور، درایوهای صنعتی و نیروگاه‌های خورشیدی و سانورتر؛ با عیب‌یابی دقیق و تست تخصصی.",
     "meta_description": "خدمات اینورتر آسانسور، درایو صنعتی، نیروگاه خورشیدی و سانورتر در الکتروگلد.",
        "phone": "02140228578", "mobile": "09998703705", "email": "info@electrogold.ir",
        "address": "تهران، پاسداران، میدان فرخی یزدی، پلاک ۶، واحد ۶", "city": "تهران", "org_name": "الکتروگلد",
      "opening_hours_text": "شنبه تا پنجشنبه 8 الی 18"},
    {"language": "en", "site_title": "ElectroGold", "tagline": "Inverter, drive and solar services",
     "hero_title": "Elevator, industrial drive and solar inverter services",
     "hero_subtitle": "Elevator inverters, industrial drives, solar plants and inverters—with precise diagnostics and specialist testing.",
     "meta_description": "Elevator inverter, industrial drive and solar inverter services from ElectroGold.",
        "phone": "02140228578", "mobile": "09998703705", "email": "info@electrogold.ir",
        "address": "Unit 6, No. 6, Farrokhi Yazdi Square, Pasdaran, Tehran, Iran", "city": "Tehran", "org_name": "ElectroGold",
      "opening_hours_text": "Sat–Thu, 8:00–18:00"},
]

PAGE_SEO = [
    {"page": "home", "focus_keyword_fa": "خدمات تعمیر درایو", "focus_keyword_en": "drive repair services",
     "seo_title_fa": "خدمات اینورتر، درایو و خورشیدی | الکتروگلد",
     "seo_title_en": "Inverter, Drive & Solar Services | ElectroGold"},
    {"page": "services", "focus_keyword_fa": "خدمات تعمیر درایو", "focus_keyword_en": "drive repair services",
     "seo_title_fa": "خدمات اینورتر آسانسور، درایو صنعتی و خورشیدی | الکتروگلد",
     "seo_title_en": "Elevator, Industrial Drive & Solar Services | ElectroGold",
     "seo_description_fa": "خدمات اینورتر آسانسور، درایو صنعتی، نیروگاه خورشیدی و سانورتر در الکتروگلد.",
     "seo_description_en": "Elevator inverters, industrial drives, solar plants and inverters.",
     "intro_fa": "خدمات اینورتر آسانسور، درایوهای صنعتی و نیروگاه‌های خورشیدی و سانورتر.",
     "intro_en": "Elevator inverters, industrial drives, solar plants and inverters."},
    {"page": "brands", "focus_keyword_fa": "تعمیر اینورتر یاسکاوا", "focus_keyword_en": "yaskawa inverter repair",
     "seo_title_fa": "برندهای تحت پوشش: یاسکاوا، مونارک، دلتا | الکتروگلد",
     "seo_title_en": "Supported Brands: Yaskawa, Monarch, Delta | ElectroGold"},
    {"page": "articles", "focus_keyword_fa": "آموزش تعمیر اینورتر", "focus_keyword_en": "inverter troubleshooting guide",
     "seo_title_fa": "مقالات آموزشی تعمیر و عیب‌یابی اینورتر | الکتروگلد",
     "seo_title_en": "Inverter Troubleshooting Guides | ElectroGold"},
    {"page": "about", "seo_title_fa": "درباره الکتروگلد | متخصص تعمیر اینورتر", "seo_title_en": "About ElectroGold | Inverter Repair Specialists"},
    {"page": "contact", "seo_title_fa": "تماس و ثبت درخواست تعمیر اینورتر | الکتروگلد",
     "seo_title_en": "Contact & Repair Request | ElectroGold"},
]

# Questions keyed by their Persian text. `service` attaches one to a service
# page; `home` puts it in the homepage FAQ.
FAQS = [
    {"home": True, "question_fa": "هزینه بررسی و تعمیر اینورتر و درایو چقدر است؟",
     "answer_fa": "بررسی و عیب‌یابی اولیه دستگاه در الکتروگلد رایگان است. پس از تحویل و پذیرش دستگاه، کارشناسان فنی آن را بررسی می‌کنند و نتیجه عیب‌یابی، هزینه قطعات موردنیاز و اجرت تعمیر را به‌صورت شفاف به شما اعلام می‌کنند. تعمیر فقط پس از تأیید شما آغاز می‌شود؛ اگر برآورد هزینه را نپذیرید، تعمیر انجام نمی‌شود. مبلغ نهایی به نوع دستگاه، ایراد شناسایی‌شده و قطعات موردنیاز بستگی دارد. اگر هزینه یا دامنه کار در جریان تعمیر تغییر کند، پیش از انجام کار اضافه، تأیید شما گرفته می‌شود.",
     "question_en": "How much do inverter and drive diagnostics and repair cost?",
     "answer_en": "Initial diagnostics are free. After your device is received and accepted, our technicians will share their findings and a clear estimate for parts and labor. Repair begins only with your approval, and any change in cost or scope is approved before additional work."},
    {"home": True, "question_fa": "عیب‌یابی و تعمیر اینورتر و درایو چقدر زمان می‌برد؟",
     "answer_fa": "پس از رسیدن و پذیرش دستگاه در مجموعه، نتیجه عیب‌یابی اولیه و برآورد هزینه در همان روز اعلام می‌شود. این زمان فقط بررسی اولیه و اعلام هزینه را شامل می‌شود و به‌معنای پایان تعمیر یا آماده‌شدن دستگاه در همان روز نیست. مدت تعمیر پس از مشخص‌شدن نوع خرابی، موجودبودن قطعات و تأیید شما برآورد می‌شود؛ زمان تقریبی تعمیر و تحویل نیز هنگام اعلام نتیجه عیب‌یابی به شما گفته خواهد شد.",
     "question_en": "How long do inverter and drive diagnostics and repair take?",
     "answer_en": "After the device arrives and is accepted, the initial diagnostic result and repair estimate are provided the same day. This covers the initial assessment only and does not mean the repair will be completed or the device will be ready that day. Repair time is estimated after the fault and parts availability are known and you approve the repair; the estimated repair and delivery time will be shared with the diagnostic result."},
    {"home": True, "question_fa": "آیا تعمیر دستگاه شامل گارانتی می‌شود؟",
     "answer_fa": "بسته به نوع دستگاه و تعمیر انجام‌شده، در صورت نیاز گارانتی کتبی ارائه می‌کنیم. مدت و شرایط گارانتی را پیش از شروع تعمیر با شما شفاف هماهنگ می‌کنیم تا با خیال آسوده برای تعمیر دستگاه تصمیم بگیرید.",
     "question_en": "Does the repair come with a warranty?",
     "answer_en": "Depending on the device and the repair performed, we can provide a written warranty when applicable. We will clearly discuss the warranty period and terms with you before starting the repair."},
    {"home": True, "question_fa": "تعمیر دستگاه در محل انجام می‌شود یا باید به کارگاه الکتروگلد ارسال شود؟",
     "answer_fa": "بسته به نوع دستگاه، ایراد و شرایط محل، می‌توانیم تعمیر را در محل شما انجام دهیم یا دستگاه را در کارگاه الکتروگلد بررسی و تعمیر کنیم. کافی است نوع دستگاه، برند و مدل، شرح مشکل و نشانی را به ما بگویید تا کارشناسان روش مناسب را با شما هماهنگ کنند.",
     "question_en": "Can you repair the device on-site, or should I send it to your workshop?",
     "answer_en": "Depending on the device, the fault, and the site conditions, we can repair it at your location or inspect and repair it at ElectroGold's workshop. Share the device type, brand and model, a description of the issue, and your location so our team can coordinate the suitable option with you."},
    {"home": True, "question_fa": "چه برندهایی را تعمیر می‌کنید؟",
     "answer_fa": "الکتروگلد انواع درایو و اینورتر صنعتی، آسانسوری و خورشیدی را می‌پذیرد. برندهای درج‌شده در فهرست خدمات عبارت‌اند از:\n\nاینورترهای آسانسوری: Siemens (زیمنس)، Delta (دلتا)، Yaskawa (یاسکاوا)، LS (ال‌اس)، Fuji (فوجی)، Danfoss (دانفوس)، ABB (ای‌بی‌بی)، INVT (اینووت)، SBT (اس‌بی‌تی)، Monarch (مونارک)، QMA، HPMont (اچ‌پی‌مونت) و ZIEHL-ABEGG (زیلابگ).\n\nدرایوهای صنعتی: Siemens، Schneider (اشنایدر)، Danfoss، ABB، LS، Fuji و Inovance (اینوونس).\n\nاینورترهای خورشیدی: Growatt (گراوات)، SolarX (سولارکس)، Voltronic (ولترونیک)، SMA، Fronius (فرونیوس)، Huawei (هواوی)، Sungrow (سانگرو)، ABB، GoodWe (گودوی)، Solis (سولیس)، Sofar (سوفار) و MUST (ماست). اصطلاح «سانورتر» فقط برای مدل‌هایی به‌کار می‌رود که از این نوع هستند.\n\nپذیرش نهایی به مدل دستگاه و امکان بررسی فنی آن بستگی دارد. برای اطمینان از پوشش مدل خود، نام برند و مدل دقیق را هنگام تماس اعلام کنید.",
     "question_en": "Which brands do you repair?",
     "answer_en": "ElectroGold accepts industrial, elevator, and solar inverters. Supported elevator-drive brands include Siemens, Delta, Yaskawa, LS, Fuji, Danfoss, ABB, INVT, SBT, Monarch, QMA, HPMont, and ZIEHL-ABEGG. Industrial-drive brands include Siemens, Schneider, Danfoss, ABB, LS, Fuji, and Inovance. Supported solar inverter brands include Growatt, SolarX, Voltronic, SMA, Fronius, Huawei, Sungrow, ABB, GoodWe, Solis, Sofar, and MUST. The term 'sanverter' applies only to models of that type. Acceptance depends on the exact model and whether it can be technically assessed; please provide the brand and model when you contact us."},
    {"home": True, "question_fa": "چطور می‌توانم دستگاه را برای تعمیر به الکتروگلد تحویل بدهم؟",
     "answer_fa": "هر روشی برایتان راحت‌تر است، همان را انتخاب کنید: دستگاه را برای ما ارسال کنید، حضوری تحویل دهید یا با ما هماهنگ کنید تا برای تحویل‌گرفتن آن به محل شما بیاییم. کافی است پیش از ارسال یا درخواست جمع‌آوری، با ما تماس بگیرید و شهر، نشانی و مشخصات دستگاه را بگویید تا روش و زمان تحویل و هزینهٔ احتمالی هماهنگ شود. بعد از پذیرش دستگاه، نتیجهٔ عیب‌یابی و برآورد هزینه را پیش از شروع تعمیر به شما اعلام می‌کنیم.",
     "question_en": "How can I get my device to ElectroGold for repair?",
     "answer_en": "Choose whichever option is most convenient: send the device to us, bring it in person, or contact us to arrange a pickup from your location. Before shipping it or requesting pickup, call us with your city, address, and device details so we can coordinate the delivery method, timing, and any applicable cost. After we accept the device, we will share the diagnostic findings and repair estimate before starting any work."},
    {"home": True, "question_fa": "برای بررسی دستگاه چه اطلاعاتی بفرستم؟",
     "answer_fa": "برای اینکه کارشناسان‌مان بهتر راهنمایی‌تان کنند، اگر در دسترس دارید، نوع دستگاه، برند و مدل، عکس واضح از پلاک مشخصات، کد خطا و توضیح کوتاهی از زمان و شرایط بروز مشکل را در فرم ثبت درخواست بنویسید یا هنگام تماس اعلام کنید. لازم نیست همهٔ این موارد را داشته باشید؛ هر اطلاعاتی که در دسترس‌تان است برای شروع راهنمایی کمک‌کننده است.",
     "question_en": "What information should I provide about my device?",
     "answer_en": "To help our technicians guide you, please provide the device type, brand and model, a clear photo of its rating plate, any error code, and a brief description of when and under what conditions the problem occurs, if available. You do not need to have every detail; whatever information you can provide will help us get started."},
    {"service": "elevator-inverter-repair", "question_fa": "علائم خرابی اینورتر آسانسور چیست؟",
     "answer_fa": "توقف ناگهانی کابین، تکان هنگام حرکت یا توقف، نمایش کد خطا روی درایو و صدای غیرعادی موتور از رایج‌ترین علائم هستند.",
     "question_en": "What are the signs of a failing elevator inverter?",
     "answer_en": "Sudden stops, jerky starts or stops, fault codes on the drive display and unusual motor noise are the most common signs."},
    {"service": "solar-inverter-repair", "question_fa": "چرا سانورتر گرووات به شبکه وصل نمی‌شود؟",
     "answer_fa": "ولتاژ یا فرکانس خارج از محدوده شبکه، خرابی رله خروجی یا مشکل عایقی پنل‌ها از دلایل رایج است که با عیب‌یابی مشخص می‌شود.",
     "question_en": "Why won't my Growatt inverter connect to the grid?",
     "answer_en": "Out-of-range grid voltage or frequency, a failed output relay or panel insulation faults are common causes, found during diagnostics."},
]



class Command(BaseCommand):
    help = "Seed this site's content, and demo accounts unless --no-demo."

    def add_arguments(self, parser):
        parser.add_argument("--no-demo", action="store_false", dest="demo",
                            help="Seed content only -- no demo users.")
        parser.add_argument("--refresh-images", action="store_true",
                            help="Look images up again for records that already have one.")
        parser.add_argument("--fresh", action="store_true",
                            help="Local development only: restore seeded values, reset demo "
                                 "passwords, and rebuild demo data from scratch.")

    def handle(self, *args, **options):
        from apps.content.models import Brand, Service
        from apps.seo.models import GlobalSeoSetting, SiteSetting
        self.refresh_images = options["refresh_images"]
        existing_images = set(Service.objects.exclude(image="").values_list("slug", flat=True))
        existing_images |= set(Brand.objects.exclude(logo="").values_list("slug", flat=True))
        images = self.find_images(
            SERVICES + BRANDS,
            "slug",
            options["refresh_images"],
            have=existing_images,
        )
        self.fresh = options["fresh"]
        with transaction.atomic():
            if options["demo"]:
                self.seed_demo(fresh=options["fresh"])
            self.seed_services(images)
            self.seed_brands(images)
            self.seed_articles(images)
            self.seed_seo()
        self.stdout.write(self.style.SUCCESS(
            "Seeded demo data." if options["demo"] else "Nothing to seed."))

    # -- images ----------------------------------------------------------

    def find_images(self, records, key, refresh, have=frozenset()):
        """Return {record key: image result} for records that need a picture.

        Each record is a dict carrying either a literal `image_url` or an
        `image_query` to look up. Best effort throughout: a failed lookup
        leaves a record out of the returned mapping, which keeps whatever image
        it already has.
        """
        wanted = [r for r in records if refresh or r[key] not in have]
        if not wanted:
            return {}

        # A record that ships its own URL is already answered: no request, and
        # no dependence on the image service being up or on the port it was
        # started with. The rest go to the finder.
        images = {r[key]: {"url": r["image_url"]} for r in wanted if r.get("image_url")}
        wanted = [r for r in wanted if not r.get("image_url")]
        if not wanted:
            return images

        # One request per distinct query, so records sharing a query cost one
        # lookup between them.
        queries = list(dict.fromkeys([r["image_query"] for r in wanted] + [FALLBACK_IMAGE_QUERY]))
        results = {query: self.search(query) for query in queries}
        # Non-article records can borrow a generic image as a last resort.
        # Articles must not: an unrelated stand-in is worse than keeping the
        # current image until a result for that article's own query is found.
        spare_candidates = results[FALLBACK_IMAGE_QUERY] or [
            image for query in queries for image in results[query]]
        spares = []
        seen_spares = set()
        for image in spare_candidates:
            url = image.get("url")
            if url and url not in seen_spares:
                spares.append(image)
                seen_spares.add(url)
        if not spares:
            self.stdout.write(self.style.WARNING(
                "No unique images found; records keep whatever image they already have."))

        used_urls = {image.get("url") for image in images.values()
                     if isinstance(image, dict) and image.get("url")}
        for record in wanted:
            found = next((image for image in results[record["image_query"]]
                          if image.get("url") and image["url"] not in used_urls), None)
            if found is None and record[key] not in ARTICLE_SLUGS:
                found = next((image for image in spares if image["url"] not in used_urls), None)
            if found:
                images[record[key]] = found
                used_urls.add(found["url"])
        return images

    def search(self, query):
        try:
            response = requests.post(f"{app_settings.IMAGE_FINDER_URL}/search",
                                     json={"query": query, "provider": "duckduckgo"},
                                     timeout=app_settings.IMAGE_FINDER_TIMEOUT)
            response.raise_for_status()
            return [image for image in response.json().get("images", []) if image.get("url")]
        except (requests.RequestException, ValueError) as exc:
            self.stdout.write(self.style.WARNING(f"Image lookup failed for {query!r}: {exc}"))
            return []

    # -- demo data -------------------------------------------------------

    def upsert(self, model, lookup, values):
        """Create the row, or fill only its blank fields -- unless --fresh.

        Content and SEO fields belong to the editors once the site is live; a
        rerun that rewrote them would silently undo the SEO specialist's work.
        Filling blanks still lets a new seeded field reach existing rows.
        """
        obj = model.objects.filter(**lookup).first()
        if obj is None:
            return model.objects.create(**lookup, **values)
        changed = [k for k, v in values.items()
                   if (self.fresh or getattr(obj, k) in ("", None)) and getattr(obj, k) != v]
        for k in changed:
            setattr(obj, k, values[k])
        if changed:
            obj.save(update_fields=changed)
        return obj

    @staticmethod
    def image_for(images, record):
        found = images.get(record["slug"])
        url = found.get("url", "") if isinstance(found, dict) else (found or "")
        return url or record.get("image_url", "")

    @staticmethod
    def fields(record, names):
        return {n: record[n] for n in names if n in record}

    def seed_services(self, images):
        from apps.content.models import Service
        names = ("category", "title_fa", "title_en", "summary_fa", "summary_en", "body_fa", "body_en",
                 "seo_title_fa", "seo_title_en", "seo_description_fa", "seo_description_en",
                 "focus_keyword_fa", "focus_keyword_en")
        # The public service catalogue is explicitly curated in SERVICES. Keep
        # its names, summaries and order aligned with that list on existing
        # databases too; longer editorial body/SEO fields remain editor-owned.
        catalogue_fields = ("category", "title_fa", "title_en", "summary_fa", "summary_en", "ordering", "published")
        for i, r in enumerate(SERVICES):
            service = self.upsert(Service, {"slug": r["slug"]}, {
                **self.fields(r, names), "image": self.image_for(images, r), "ordering": i,
                "schema_type": "Service"})
            sync_fields = catalogue_fields
            if r["slug"] in {"elevator-inverter-repair", "industrial-inverter-repair", "solar-inverter-repair"}:
                # These service pages' long-form copy was supplied as approved
                # Word documents, so keep their bodies and SEO fields synced.
                sync_fields += ("body_fa", "body_en", "seo_title_fa", "seo_title_en",
                                "seo_description_fa", "seo_description_en")
            changed = []
            for field in sync_fields:
                value = i if field == "ordering" else True if field == "published" else r[field]
                if getattr(service, field) != value:
                    setattr(service, field, value)
                    changed.append(field)
            if changed:
                service.save(update_fields=changed)
        Service.objects.exclude(slug__in=[r["slug"] for r in SERVICES]).update(published=False)

    def seed_brands(self, images):
        from apps.content.models import Brand, Service
        names = ("category", "name_fa", "name_en", "description_fa", "description_en", "content_fa", "content_en",
                 "seo_title_fa", "seo_title_en", "seo_description_fa", "seo_description_en")
        for i, r in enumerate(BRANDS):
            logo = self.image_for(images, r)
            ordering = BRAND_ORDER.get(r["slug"], i)
            b = self.upsert(Brand, {"slug": r["slug"]}, {
                **self.fields(r, names), "logo": logo, "ordering": ordering,
                "schema_type": "Brand"})
            # Keep the short repair summaries synced on existing listings too;
            # ordinary seed upserts otherwise preserve already-filled copy.
            sync_fields = ("category", "description_fa", "description_en", "content_fa", "content_en")
            if r["slug"] in {"kyuma", "inovance"}:
                # QMA's corrected name and concise page copy must also replace
                # the former incorrect brand name in existing records. Keep
                # Inovance's expanded elevator-service coverage in sync too.
                sync_fields = names
            changed_fields = [field for field in sync_fields if getattr(b, field) != r[field]]
            for field in changed_fields:
                setattr(b, field, r[field])
            if changed_fields:
                b.save(update_fields=changed_fields)
            if not b.published:
                b.published = True
                b.save(update_fields=["published"])
            changed = []
            if b.logo != logo:
                b.logo = logo
                changed.append("logo")
            if b.ordering != ordering:
                b.ordering = ordering
                changed.append("ordering")
            if changed:
                b.save(update_fields=changed)
            related_services = list(Service.objects.filter(slug__in=r.get("services", [])))
            if self.fresh or r["slug"] == "invt" or not b.services.exists():
                b.services.set(related_services)
            else:
                # Keep previously curated links while adding newly supported
                # service relationships, such as Delta's elevator coverage.
                b.services.add(*related_services)
            if r["slug"] == "fronius":
                retired_welding_service = Service.objects.filter(slug="welding-inverter-repair").first()
                if retired_welding_service:
                    b.services.remove(retired_welding_service)
        Brand.objects.exclude(slug__in=[r["slug"] for r in BRANDS]).update(published=False)

    def seed_articles(self, images):
        from datetime import timedelta
        from django.utils import timezone
        from apps.content.models import Article, Brand, Service
        names = ("title_fa", "title_en", "excerpt_fa", "excerpt_en", "body_fa", "body_en", "author",
                 "seo_title_fa", "seo_title_en", "seo_description_fa", "seo_description_en")
        for i, r in enumerate(ARTICLES):
            a = self.upsert(Article, {"slug": r["slug"]}, {
                **self.fields(r, names), "image": article_image_path(r),
                "article_type": r.get("article_type", "brand_specific" if r.get("brands") else "general"),
                "published_at": timezone.now() - timedelta(days=r.get("published_days_ago", i)),
                "schema_type": "BlogPosting"})
            refreshed_image = article_image_path(r)
            if refreshed_image and (
                self.fresh or self.refresh_images
                or a.image in ("", LEGACY_ARTICLE_IMAGE_URL)
                or a.image in PREVIOUS_ARTICLE_IMAGE_PATHS
            ) and a.image != refreshed_image:
                a.image = refreshed_image
                a.save(update_fields=["image"])
            related_brand_slugs = tuple(
                "inovance" if slug == "invt" else slug for slug in r.get("brands", [])
            )
            if self.fresh:
                a.services.set(Service.objects.filter(slug__in=r.get("services", [])))
                a.brands.set(Brand.objects.filter(slug__in=related_brand_slugs))
            else:
                # Add the relationships declared by seed data without removing
                # links an editor may have added directly in the CMS.
                a.services.add(*Service.objects.filter(slug__in=r.get("services", [])))
                a.brands.add(*Brand.objects.filter(slug__in=related_brand_slugs))
        # The public brand catalogue uses Inovance in place of the retired INVT
        # listing, so migrate old manual and seeded INVT relations there.
        invt = Brand.objects.filter(slug="invt").first()
        inovance = Brand.objects.filter(slug="inovance", published=True).first()
        if invt and inovance:
            for article in Article.objects.filter(brands=invt):
                article.brands.remove(invt)
                article.brands.add(inovance)
        # Keep the catalogue focused on brand-specific fault-code articles.
        Article.objects.filter(slug__in=NON_ERROR_ARTICLE_SLUGS).delete()
        # Only retire seed-managed articles; do not unpublish editorial records
        # created directly in the CMS or imported from content backups.
        Article.objects.filter(slug__in=MANAGED_ARTICLE_SLUGS).exclude(
            slug__in=[r["slug"] for r in ARTICLES]).update(published=False)

    def seed_seo(self):
        from apps.content.models import FaqItem, Service
        from apps.seo.models import GlobalSeoSetting, PageSeo, SiteSetting
        for r in SITE_SETTINGS:
            setting = self.upsert(
                SiteSetting, {"language": r["language"]},
                {k: v for k, v in r.items() if k != "language"})
            # Contact details are operational data, not editorial copy: keep
            # existing records in sync when the company details change.
            for field in ("phone", "mobile", "email", "address"):
                if getattr(setting, field) != r[field]:
                    setattr(setting, field, r[field])
                    setting.save(update_fields=[field])
            if setting.opening_hours_text != r["opening_hours_text"]:
                setting.opening_hours_text = r["opening_hours_text"]
                setting.save(update_fields=["opening_hours_text"])
            retired_service_copy_fields = ("tagline", "hero_title", "hero_subtitle", "meta_description")
            changed = [field for field in retired_service_copy_fields
                       if ("automation" in getattr(setting, field).lower()
                           or "اتوماسیون" in getattr(setting, field))
                       and getattr(setting, field) != r[field]]
            for field in changed:
                setattr(setting, field, r[field])
            if changed:
                setting.save(update_fields=changed)
        GlobalSeoSetting.load()
        self.upsert(GlobalSeoSetting, {"pk": 1}, {"org_schema_name": "ElectroGold"})
        for r in PAGE_SEO:
            page = self.upsert(PageSeo, {"page": r["page"]}, {k: v for k, v in r.items() if k != "page"})
            if r["page"] == "services":
                # Keep the services landing-page summary and search metadata in
                # sync with the three public service categories.
                fields = ("focus_keyword_fa", "focus_keyword_en", "seo_title_fa", "seo_title_en",
                          "seo_description_fa", "seo_description_en", "intro_fa", "intro_en")
                changed = [field for field in fields if getattr(page, field) != r[field]]
                for field in changed:
                    setattr(page, field, r[field])
                if changed:
                    page.save(update_fields=changed)
            elif r["page"] == "home":
                fields = ("seo_title_fa", "seo_title_en")
                changed = [field for field in fields if getattr(page, field) != r[field]]
                for field in changed:
                    setattr(page, field, r[field])
                if changed:
                    page.save(update_fields=changed)
        for i, r in enumerate(FAQS):
            service = Service.objects.filter(slug=r["service"]).first() if r.get("service") else None
            faq = self.upsert(FaqItem, {"question_fa": r["question_fa"]}, {
                "answer_fa": r["answer_fa"], "question_en": r["question_en"], "answer_en": r["answer_en"],
                "show_on_home": r.get("home", False), "service": service, "ordering": i})
            if r["question_fa"] in {
                "هزینه بررسی و تعمیر اینورتر و درایو چقدر است؟",
                "عیب‌یابی و تعمیر اینورتر و درایو چقدر زمان می‌برد؟",
                "آیا تعمیر دستگاه شامل گارانتی می‌شود؟",
                "تعمیر دستگاه در محل انجام می‌شود یا باید به کارگاه الکتروگلد ارسال شود؟",
                "چه برندهایی را تعمیر می‌کنید؟",
                "چطور می‌توانم دستگاه را برای تعمیر به الکتروگلد تحویل بدهم؟",
                "برای بررسی دستگاه چه اطلاعاتی بفرستم؟",
            }:
                canonical_values = {
                    "answer_fa": r["answer_fa"],
                    "question_en": r["question_en"],
                    "answer_en": r["answer_en"],
                    "show_on_home": r.get("home", False),
                    "ordering": i,
                }
                corrected_fields = [field for field, value in canonical_values.items()
                                    if getattr(faq, field) != value]
                for field in corrected_fields:
                    setattr(faq, field, canonical_values[field])
                if corrected_fields:
                    faq.save(update_fields=corrected_fields)
        retired_home_questions = [
            "تعمیر اینورتر چقدر زمان می‌برد؟",
            "آیا تعمیرات الکتروگلد گارانتی دارد؟",
            "اینورتر چه برندهایی را تعمیر می‌کنید؟",
            "برای خرابی اضطراری آسانسور چه کنم؟",
            "هزینه بررسی و تعمیر اینورتر چقدر است؟",
            "عیب‌یابی و تعمیر اینورتر چقدر زمان می‌برد؟",
            "چه برندها و انواعی از درایو را تعمیر می‌کنید؟",
            "در خرابی اضطراری اینورتر چه اقدامی انجام دهم؟",
        ]
        FaqItem.objects.filter(question_fa__in=retired_home_questions).update(show_on_home=False)
        FaqItem.objects.filter(
            question_fa__in=(
                "در خرابی اضطراری اینورتر چه اقدامی انجام دهم؟",
                "برای خرابی اضطراری آسانسور چه کنم؟",
            )
        ).update(published=False)

    def seed_demo(self, *, fresh):
        customer = self.seed_user("CUSTOMER", "customer@example.com", "customer-password", fresh=fresh)
        self.seed_user("ADMIN", "admin@example.com", "admin-password", fresh=fresh, staff=True)
        return customer

    def seed_user(self, prefix, email, password, *, fresh, staff=False):
        email = getattr(app_settings, f"SEED_{prefix}_EMAIL", email)
        user, created = get_user_model().objects.get_or_create(
            email=email, defaults={"username": email.split("@")[0], "is_active": True})
        # Resetting a password on every run would silently undo a local change.
        if created or fresh:
            user.set_password(getattr(app_settings, f"SEED_{prefix}_PASSWORD", password))
        user.is_active = True
        user.is_staff = user.is_superuser = staff
        user.save()
        return user

