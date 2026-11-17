
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
from apps.common.management.commands.elevator_service_content import ELEVATOR_SERVICE_BODY_EN, ELEVATOR_SERVICE_BODY_FA
from apps.common.management.commands.industrial_service_content import INDUSTRIAL_SERVICE_BODY_EN, INDUSTRIAL_SERVICE_BODY_FA
from apps.common.management.commands.solar_service_content import SOLAR_SERVICE_BODY_EN, SOLAR_SERVICE_BODY_FA
from apps.common.management.commands.welding_service_content import WELDING_SERVICE_BODY_EN, WELDING_SERVICE_BODY_FA

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
    "welding-inverter-repair": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=1200&q=80",
    "automation-and-control-service": "https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=1200&q=80",
}
BRAND_LOGO_PATHS = {
    "siemens": "/brands/siemens.svg",
    "schneider": "/brands/schneider.svg",
    "ls": "/brands/ls.svg",
    "fuji": "/brands/fuji.svg",
    "danfoss": "/brands/danfoss.svg",
    "abb": "/brands/abb.svg",
    "invt": "/brands/invt.svg",
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
    "saba-electric": "/brands/saba-electric.svg",
    "iran-trans": "/brands/iran-trans.svg",
    "edon": "/brands/edon.svg",
    "tosan": "/brands/tosan.svg",
    "miller": "/brands/miller.svg",
    "jasic": "/brands/jasic.svg",
    "arva": "/brands/arva.svg",
    "yaskawa": "/brands/yaskawa.svg",
    "monarch": "/brands/monarch.svg",
    "hpmont": "/brands/hpmont.svg",
    "zilabeg": "/brands/zilabeg.svg",
    "delta": "/brands/delta.svg",
    "inovance": "/brands/inovance.svg",
    "growatt": "/brands/growatt.svg",
}
ARTICLE_IMAGE_URL = "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=1200&q=80"

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
    {"slug": "welding-inverter-repair", "category": "industrial",
     "title_fa": "خدمات تجهیزات جوشکاری", "title_en": "Welding Equipment Services",
     "summary_fa": "تعمیر و بازسازی اینورتر جوشکاری، تثبیت جریان خروجی، عیب‌یابی برد قدرت و تست زیر بار.",
     "summary_en": "Welding-inverter repair, output-current stabilization, power-board diagnostics and load testing.",
     "body_fa": WELDING_SERVICE_BODY_FA,
     "body_en": WELDING_SERVICE_BODY_EN,
     "seo_title_fa": "تعمیر تخصصی اینورتر دستگاه جوش | الکتروگلد", "seo_title_en": "Specialist Welding-Inverter Repair | ElectroGold",
     "seo_description_fa": "تعمیر اینورتر جوشکاری با تثبیت جریان، بازسازی برد قدرت و کنترل و تست عملکرد زیر بار.",
     "seo_description_en": "Welding-inverter repair with current stabilization, power and control board reconditioning, and load testing.",
     "image_query": "industrial welding equipment repair workshop"},
    {"slug": "automation-and-control-service", "category": "industrial",
     "title_fa": "خدمات اتوماسیون و کنترل", "title_en": "Automation & Control Services",
     "summary_fa": "عیب‌یابی و سرویس درایوها، کنترلرها، تابلوها و سامانه‌های اتوماسیون صنعتی.",
     "summary_en": "Diagnostics and service for drives, controllers, panels and industrial automation systems.",
     "body_fa": "خدمات اتوماسیون و کنترل شامل عیب‌یابی درایو و کنترلر، بررسی سیگنال‌های ورودی و خروجی، تنظیم پارامترها و تست عملکرد سامانه است.",
     "body_en": "Automation and control services include drive and controller diagnostics, I/O signal checks, parameter configuration and system testing.",
     "seo_title_fa": "خدمات اتوماسیون و کنترل صنعتی | الکتروگلد", "seo_title_en": "Industrial Automation & Control Services | ElectroGold",
     "seo_description_fa": "عیب‌یابی و سرویس درایو، کنترلر، تابلو و سامانه‌های اتوماسیون صنعتی.",
     "seo_description_en": "Diagnostics and service for industrial drives, controllers, panels and automation systems.",
     "image_query": "industrial automation control panel PLC technician"},
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
     "description_fa": "تعمیر اینورتر اینوونس.", "description_en": "Inovance inverter repair.",
     "content_fa": "پشتیبانی درایوهای Inovance.", "content_en": "Inovance drive support.",
     "seo_title_fa": "تعمیر اینورتر اینوونس | الکتروگلد", "seo_title_en": "Inovance Inverter Repair | ElectroGold",
     "seo_description_fa": "عیب‌یابی و تعمیر اینوونس.", "seo_description_en": "Inovance diagnostics and repair.",
     "image_query": "industrial automation control panel", "services": ["industrial-inverter-repair"]},
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
    {"slug": "invt", "category": "elevator", "name_fa": "اینوت", "name_en": "INVT",
     "description_fa": "خدمات فنی و تعمیر درایوهای اینوت.", "description_en": "Technical service and repair for INVT drives.",
     "content_fa": "عیب‌یابی خطاها و تعمیر درایوهای INVT در کاربردهای آسانسوری.", "content_en": "Fault diagnosis and repair for INVT drives in elevator applications.",
     "seo_title_fa": "تعمیر درایو اینوت | الکتروگلد", "seo_title_en": "INVT Drive Repair | ElectroGold",
     "seo_description_fa": "عیب‌یابی و تعمیر تخصصی درایوهای اینوت.", "seo_description_en": "Specialist diagnostics and repair for INVT drives.",
     "image_query": "INVT elevator inverter", "services": ["elevator-inverter-repair"]},
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
      "image_query": "Fronius solar inverter", "services": ["solar-inverter-repair", "welding-inverter-repair"]},
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
    {"slug": "saba-electric", "category": "industrial", "name_fa": "صبا الکتریک", "name_en": "Saba Electric",
      "description_fa": "خدمات تخصصی عیب‌یابی و تعمیر تجهیزات جوشکاری صبا الکتریک.", "description_en": "Specialist diagnostics and repair for Saba Electric welding equipment.",
      "content_fa": "پشتیبانی فنی دستگاه‌های جوش صبا الکتریک و عیب‌یابی بخش‌های قدرت و کنترل.", "content_en": "Technical support for Saba Electric welders, including power and control diagnostics.",
      "seo_title_fa": "تعمیر دستگاه جوش صبا الکتریک | الکتروگلد", "seo_title_en": "Saba Electric Welder Repair | ElectroGold",
      "seo_description_fa": "عیب‌یابی و تعمیر تخصصی دستگاه‌های جوش صبا الکتریک.", "seo_description_en": "Specialist troubleshooting and repair for Saba Electric welding machines.",
      "image_query": "Saba Electric welding machine", "services": ["welding-inverter-repair"]},
    {"slug": "iran-trans", "category": "industrial", "name_fa": "ایران ترانس", "name_en": "Iran Trans",
      "description_fa": "عیب‌یابی و تعمیر دستگاه‌های جوش و تجهیزات ایران ترانس.", "description_en": "Diagnostics and repair for Iran Trans welding machines and equipment.",
      "content_fa": "خدمات تعمیر و پشتیبانی تجهیزات جوشکاری ایران ترانس.", "content_en": "Repair and support services for Iran Trans welding equipment.",
      "seo_title_fa": "تعمیر دستگاه جوش ایران ترانس | الکتروگلد", "seo_title_en": "Iran Trans Welder Repair | ElectroGold",
      "seo_description_fa": "تعمیر تخصصی دستگاه‌های جوش ایران ترانس با تست عملکرد.", "seo_description_en": "Specialist repair and operational testing for Iran Trans welders.",
      "image_query": "Iran Trans welding equipment", "services": ["welding-inverter-repair"]},
    {"slug": "edon", "category": "industrial", "name_fa": "ادون", "name_en": "Edon",
      "description_fa": "خدمات عیب‌یابی و تعمیر دستگاه‌های جوش ادون.", "description_en": "Edon welding-machine diagnostics and repair services.",
      "content_fa": "عیب‌یابی برد قدرت و کنترل و تعمیر تجهیزات جوشکاری ادون.", "content_en": "Power and control board diagnostics and repair for Edon welding equipment.",
      "seo_title_fa": "تعمیر دستگاه جوش ادون | الکتروگلد", "seo_title_en": "Edon Welder Repair | ElectroGold",
      "seo_description_fa": "خدمات تعمیر دستگاه جوش ادون و تست زیر بار.", "seo_description_en": "Edon welding-machine repair and load testing.",
      "image_query": "Edon inverter welder", "services": ["welding-inverter-repair"]},
    {"slug": "tosan", "category": "industrial", "name_fa": "توسن", "name_en": "Tosan",
      "description_fa": "عیب‌یابی و تعمیر تجهیزات جوشکاری توسن.", "description_en": "Tosan welding-equipment diagnostics and repair.",
      "content_fa": "پشتیبانی و تعمیر دستگاه‌های جوش توسن، از برد کنترل تا بخش قدرت.", "content_en": "Support and repair for Tosan welders, from control boards to power stages.",
      "seo_title_fa": "تعمیر دستگاه جوش توسن | الکتروگلد", "seo_title_en": "Tosan Welder Repair | ElectroGold",
      "seo_description_fa": "خدمات فنی و تعمیر دستگاه‌های جوش توسن با تست عملکرد.", "seo_description_en": "Technical repair and functional testing for Tosan welding machines.",
      "image_query": "Tosan welding machine", "services": ["welding-inverter-repair"]},
    {"slug": "miller", "category": "industrial", "name_fa": "میلر", "name_en": "Miller",
      "description_fa": "خدمات تعمیر و عیب‌یابی دستگاه‌های جوش میلر.", "description_en": "Miller welding-machine repair and diagnostics.",
      "content_fa": "عیب‌یابی و بازسازی تجهیزات جوشکاری میلر و بررسی پایداری جریان خروجی.", "content_en": "Diagnostics and reconditioning for Miller welders, including output-current stability checks.",
      "seo_title_fa": "تعمیر دستگاه جوش میلر | الکتروگلد", "seo_title_en": "Miller Welder Repair | ElectroGold",
      "seo_description_fa": "تعمیر تخصصی دستگاه‌های جوش میلر و تست کیفیت قوس و جریان.", "seo_description_en": "Specialist Miller welder repair with arc and output-current testing.",
      "image_query": "Miller welding equipment", "services": ["welding-inverter-repair"]},
    {"slug": "jasic", "category": "industrial", "name_fa": "جاسک", "name_en": "Jasic",
      "description_fa": "خدمات تخصصی عیب‌یابی و تعمیر دستگاه‌های جوش جاسک.", "description_en": "Specialist diagnostics and repair for Jasic welding machines.",
      "content_fa": "تعمیر بردهای کنترل و قدرت دستگاه‌های جوش جاسک و تست عملکرد زیر بار.", "content_en": "Control and power board repair for Jasic welders, followed by load testing.",
      "seo_title_fa": "تعمیر دستگاه جوش جاسک | الکتروگلد", "seo_title_en": "Jasic Welder Repair | ElectroGold",
      "seo_description_fa": "عیب‌یابی و تعمیر دستگاه‌های جوش جاسک با تست جریان خروجی.", "seo_description_en": "Jasic welder diagnostics and repair with output-current testing.",
      "image_query": "Jasic inverter welding machine", "services": ["welding-inverter-repair"]},
    {"slug": "arva", "category": "industrial", "name_fa": "آروا", "name_en": "Arva",
      "description_fa": "خدمات تعمیر و پشتیبانی دستگاه‌های جوش آروا.", "description_en": "Repair and technical support for Arva welding machines.",
      "content_fa": "عیب‌یابی تجهیزات جوشکاری آروا، تعمیر بخش قدرت و کنترل و تست نهایی.", "content_en": "Arva welding-equipment diagnostics, power and control repair, and final testing.",
      "seo_title_fa": "تعمیر دستگاه جوش آروا | الکتروگلد", "seo_title_en": "Arva Welder Repair | ElectroGold",
      "seo_description_fa": "تعمیر تخصصی دستگاه‌های جوش آروا با بررسی برد و تست عملکرد.", "seo_description_en": "Specialist Arva welder repair with board diagnostics and functional testing.",
      "image_query": "Arva welding equipment", "services": ["welding-inverter-repair"]},
]
BRAND_ORDER = {slug: index for index, slug in enumerate((
    "siemens", "delta", "yaskawa", "ls", "fuji", "danfoss", "abb", "invt", "sbt",
    "monarch", "kyuma", "hpmont", "zilabeg", "inovance", "growatt", "solarx",
    "voltronic", "sma", "fronius", "huawei", "sungrow", "goodwe", "solis", "sofar", "must",
    "saba-electric", "iran-trans", "edon", "tosan", "miller", "jasic", "arva",
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
for _record in ARTICLES:
    _record["image_url"] = ARTICLE_IMAGE_URL

SITE_SETTINGS = [
    {"language": "fa", "site_title": "الکتروگلد", "tagline": "خدمات درایو، تجهیزات خورشیدی، جوشکاری و اتوماسیون",
     "hero_title": "خدمات اینورتر آسانسور، درایو صنعتی، خورشیدی، جوشکاری و اتوماسیون",
     "hero_subtitle": "خدمات اینورتر آسانسور، درایوهای صنعتی، نیروگاه‌های خورشیدی و سانورتر، تجهیزات جوشکاری، اتوماسیون و کنترل؛ با عیب‌یابی دقیق و تست تخصصی.",
     "meta_description": "خدمات اینورتر آسانسور، درایو صنعتی، نیروگاه خورشیدی و سانورتر، تجهیزات جوشکاری و اتوماسیون و کنترل در الکتروگلد.",
      "phone": "09998703705", "email": "info@electrogold.ir",
      "address": "تهران، ایران", "city": "تهران", "org_name": "الکتروگلد",
     "opening_hours_text": "شنبه تا پنجشنبه، ۸ تا ۱۸"},
    {"language": "en", "site_title": "ElectroGold", "tagline": "Drive, solar, welding and automation services",
     "hero_title": "Elevator, industrial drive, solar, welding and automation services",
     "hero_subtitle": "Elevator inverters, industrial drives, solar plants and inverters, welding equipment, automation and control—with precise diagnostics and specialist testing.",
     "meta_description": "Elevator inverter, industrial drive, solar, welding equipment, automation and control services from ElectroGold.",
      "phone": "09998703705", "email": "info@electrogold.ir",
      "address": "Tehran, Iran", "city": "Tehran", "org_name": "ElectroGold",
     "opening_hours_text": "Sat–Thu, 8:00–18:00"},
]

PAGE_SEO = [
    {"page": "home", "focus_keyword_fa": "خدمات تعمیر درایو", "focus_keyword_en": "drive repair services",
     "seo_title_fa": "خدمات اینورتر، درایو، خورشیدی و اتوماسیون | الکتروگلد",
     "seo_title_en": "Inverter, Drive, Solar & Automation Services | ElectroGold"},
    {"page": "services", "focus_keyword_fa": "خدمات درایو و اتوماسیون", "focus_keyword_en": "drive and automation services",
     "seo_title_fa": "خدمات اینورتر آسانسور، درایو صنعتی و اتوماسیون | الکتروگلد",
     "seo_title_en": "Elevator, Industrial Drive & Automation Services | ElectroGold",
     "seo_description_fa": "خدمات اینورتر آسانسور، درایو صنعتی، نیروگاه خورشیدی و سانورتر، تجهیزات جوشکاری، اتوماسیون و کنترل در الکتروگلد.",
     "seo_description_en": "Elevator inverters, industrial drives, solar plants and inverters, welding equipment, automation and control services.",
     "intro_fa": "خدمات اینورتر آسانسور، درایوهای صنعتی، نیروگاه‌های خورشیدی و سانورتر، تجهیزات جوشکاری، اتوماسیون و کنترل.",
     "intro_en": "Elevator inverters, industrial drives, solar plants and inverters, welding equipment, automation and control."},
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
    {"home": True, "question_fa": "تعمیر اینورتر چقدر زمان می‌برد؟",
     "answer_fa": "بسته به نوع خرابی و در دسترس بودن قطعه متفاوت است. پس از عیب‌یابی، زمان و هزینه دقیق پیش از شروع تعمیر به شما اعلام می‌شود.",
     "question_en": "How long does an inverter repair take?",
     "answer_en": "It depends on the fault and part availability. After diagnostics you get an exact time and cost before any repair starts."},
    {"home": True, "question_fa": "آیا تعمیرات الکتروگلد گارانتی دارد؟",
     "answer_fa": "بله. هر دستگاه پس از تعمیر زیر بار تست می‌شود و خدمات انجام‌شده گارانتی دارند.",
     "question_en": "Do your repairs come with a warranty?",
     "answer_en": "Yes. Every unit is load-tested after repair and the work carries a service warranty."},
    {"home": True, "question_fa": "اینورتر چه برندهایی را تعمیر می‌کنید؟",
      "answer_fa": "درایوهای آسانسوری زیمنس، دلتا، یاسکاوا، ال‌اس، فوجی، دانفوس، ای‌بی‌بی، اینوت، اس‌بی‌تی، مونارک و QMA؛ همچنین اچ‌پی‌مونت و زیلابگ. درایوهای صنعتی دلتا، یاسکاوا، زیمنس، اشنایدر، دانفوس، ای‌بی‌بی، ال‌اس، فوجی و اینوونس؛ تجهیزات خورشیدی گراوات، سولارکس، ولترونیک، SMA، فرونیوس، هوآوی، سانگرو، ای‌بی‌بی، گودوی، سولیس، سوفار و ماست؛ و تجهیزات جوشکاری صبا الکتریک، ایران ترانس، ادون، توسن، فرونیوس، میلر، جاسک و آروا نیز پشتیبانی می‌شوند.",
     "question_en": "Which inverter brands do you repair?",
      "answer_en": "Elevator drives from Siemens, Delta, Yaskawa, LS, Fuji, Danfoss, ABB, INVT, SBT, Monarch and QMA, plus HPMont and Zilabeg; industrial drives from Delta, Yaskawa, Siemens, Schneider, Danfoss, ABB, LS, Fuji and Inovance; solar equipment from Growatt, SolarX, Voltronic, SMA, Fronius, Huawei, Sungrow, ABB, GoodWe, Solis, Sofar and MUST; and welding equipment from Saba Electric, Iran Trans, Edon, Tosan, Fronius, Miller, Jasic and Arva."},
    {"home": True, "question_fa": "برای خرابی اضطراری آسانسور چه کنم؟",
     "answer_fa": "با شماره تماس سایت تماس بگیرید یا در فرم درخواست، اضطراری بودن را ذکر کنید تا در اولویت بررسی قرار گیرد.",
     "question_en": "What should I do about an elevator emergency?",
     "answer_en": "Call us, or mention the emergency in the request form so it is handled first."},
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
        from apps.content.models import Article, Brand, Service
        from apps.seo.models import GlobalSeoSetting, SiteSetting
        images = self.find_images(SERVICES + BRANDS + ARTICLES, "slug", options["refresh_images"],
                                  have=set(Service.objects.exclude(image="").values_list("slug", flat=True)) | set(Brand.objects.exclude(logo="").values_list("slug", flat=True)) | set(Article.objects.exclude(image="").values_list("slug", flat=True)))
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
        # What a record whose own query found nothing falls back to: the
        # generic picture if that search worked, otherwise anything at all,
        # since a stand-in beats a blank tile.
        spares = results[FALLBACK_IMAGE_QUERY] or [
            image for query in queries for image in results[query]]
        if not spares:
            self.stdout.write(self.style.WARNING(
                "No images found; records keep whatever image they already have."))
            return images

        # Every seeded record ends up with an image URL.
        borrowed = 0
        for record in wanted:
            found = results[record["image_query"]]
            images[record[key]] = found[0] if found else spares[borrowed % len(spares)]
            borrowed += 0 if found else 1
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
            if r["slug"] in {"elevator-inverter-repair", "industrial-inverter-repair", "solar-inverter-repair", "welding-inverter-repair"}:
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
            if r["slug"] == "kyuma":
                # Correct the existing public listing too; normal seed upserts
                # intentionally preserve editorial copy on already-filled rows.
                corrected_fields = [field for field in names if getattr(b, field) != r[field]]
                for field in corrected_fields:
                    setattr(b, field, r[field])
                if corrected_fields:
                    b.save(update_fields=corrected_fields)
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
            if self.fresh or not b.services.exists():
                b.services.set(related_services)
            else:
                # Keep previously curated links while adding newly supported
                # service relationships, such as Delta's elevator coverage.
                b.services.add(*related_services)
        Brand.objects.exclude(slug__in=[r["slug"] for r in BRANDS]).update(published=False)

    def seed_articles(self, images):
        from datetime import timedelta
        from django.utils import timezone
        from apps.content.models import Article, Brand, Service
        names = ("title_fa", "title_en", "excerpt_fa", "excerpt_en", "body_fa", "body_en", "author",
                 "seo_title_fa", "seo_title_en", "seo_description_fa", "seo_description_en")
        for i, r in enumerate(ARTICLES):
            a = self.upsert(Article, {"slug": r["slug"]}, {
                **self.fields(r, names), "image": self.image_for(images, r),
                "published_at": timezone.now() - timedelta(days=i), "schema_type": "BlogPosting"})
            if self.fresh:
                a.services.set(Service.objects.filter(slug__in=r.get("services", [])))
                a.brands.set(Brand.objects.filter(slug__in=r.get("brands", [])))
            else:
                # Add the relationships declared by seed data without removing
                # links an editor may have added directly in the CMS.
                a.services.add(*Service.objects.filter(slug__in=r.get("services", [])))
                a.brands.add(*Brand.objects.filter(slug__in=r.get("brands", [])))
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
            # Contact details are operational data, not editorial copy: make
            # sure a changed address replaces the previous value on reruns.
            if setting.email != r["email"]:
                setting.email = r["email"]
                setting.save(update_fields=["email"])
        GlobalSeoSetting.load()
        self.upsert(GlobalSeoSetting, {"pk": 1}, {"org_schema_name": "ElectroGold"})
        for r in PAGE_SEO:
            page = self.upsert(PageSeo, {"page": r["page"]}, {k: v for k, v in r.items() if k != "page"})
            if r["page"] == "services":
                # Keep the services landing-page summary and search metadata in
                # sync with the five requested service categories.
                fields = ("focus_keyword_fa", "focus_keyword_en", "seo_title_fa", "seo_title_en",
                          "seo_description_fa", "seo_description_en", "intro_fa", "intro_en")
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
            if r["question_fa"] == "اینورتر چه برندهایی را تعمیر می‌کنید؟":
                corrected_fields = [field for field in ("answer_fa", "answer_en")
                                    if getattr(faq, field) != r[field]]
                for field in corrected_fields:
                    setattr(faq, field, r[field])
                if corrected_fields:
                    faq.save(update_fields=corrected_fields)

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

