
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
    "cooler-inverter-repair": "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=1200&q=80",
}
BRAND_IMAGE_URL = "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=800&q=80"
ARTICLE_IMAGE_URL = "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=1200&q=80"

SERVICES = [
    {"slug": "elevator-inverter-repair", "category": "elevator",
     "title_fa": "تعمیر اینورتر آسانسور", "title_en": "Elevator Inverter Repair",
     "summary_fa": "عیب‌یابی، تعمیر و نگهداری اینورترهای آسانسور یاسکاوا، مونارک، اچ‌پی‌مونت و زیلابگ.",
     "summary_en": "Troubleshooting, repair and maintenance of elevator inverters: Yaskawa, Monarch, HPMont, Zilabeg.",
     "body_fa": "تعمیر تخصصی اینورتر آسانسور شامل عیب‌یابی، تعویض قطعات و سرویس دوره‌ای.",
     "body_en": "Specialist elevator inverter repair including diagnostics, component replacement and preventive maintenance.",
     "seo_title_fa": "تعمیر اینورتر آسانسور | الکتروگلد", "seo_title_en": "Elevator Inverter Repair | ElectroGold",
     "seo_description_fa": "عیب‌یابی و تعمیر اینورتر آسانسور یاسکاوا، مونارک، اچ‌پی‌مونت و زیلابگ با ضمانت.",
     "seo_description_en": "Elevator inverter troubleshooting and repair for Yaskawa, Monarch, HPMont and Zilabeg.",
     "image_query": "elevator control panel inverter repair"},
    {"slug": "industrial-inverter-repair", "category": "industrial",
     "title_fa": "تعمیر اینورتر صنعتی", "title_en": "Industrial Inverter Repair",
     "summary_fa": "عیب‌یابی و تعمیر اینورترهای صنعتی دلتا، یاسکاوا و اینوونس.",
     "summary_en": "Troubleshooting and repair of Delta, Yaskawa and Inovance industrial inverters.",
     "body_fa": "تعمیر درایو صنعتی، رفع خطا و نگهداری پیشگیرانه خطوط تولید.",
     "body_en": "Industrial drive repair, fault clearing and preventive maintenance for production lines.",
     "seo_title_fa": "تعمیر اینورتر صنعتی | الکتروگلد", "seo_title_en": "Industrial Inverter Repair | ElectroGold",
     "seo_description_fa": "تعمیر تخصصی اینورتر صنعتی دلتا، یاسکاوا و اینوونس با تست کامل.",
     "seo_description_en": "Specialist repair of Delta, Yaskawa and Inovance industrial inverters.",
     "image_query": "industrial variable frequency drive factory"},
    {"slug": "welding-inverter-repair", "category": "industrial",
     "title_fa": "تعمیر اینورتر دستگاه جوش", "title_en": "Welding Machine Inverter Repair",
     "summary_fa": "عیب‌یابی، تعمیر و نگهداری اینورتر دستگاه‌های جوش.",
     "summary_en": "Troubleshooting, repair and maintenance of welding machine inverters.",
     "body_fa": "تعمیر تخصصی اینورتر دستگاه جوش شامل عیب‌یابی برد قدرت، تعویض IGBT و تست زیر بار.",
     "body_en": "Specialist welding inverter repair including power board diagnostics, IGBT replacement and load testing.",
     "seo_title_fa": "تعمیر اینورتر دستگاه جوش | الکتروگلد", "seo_title_en": "Welding Machine Inverter Repair | ElectroGold",
     "seo_description_fa": "عیب‌یابی و تعمیر اینورتر دستگاه جوش با تست کامل و ضمانت.",
     "seo_description_en": "Welding machine inverter troubleshooting and repair with full testing and warranty.",
     "image_query": "welding machine repair workshop"},
    {"slug": "cooler-inverter-repair", "category": "industrial",
     "title_fa": "تعمیر اینورتر کولر", "title_en": "Cooler Inverter Repair",
     "summary_fa": "عیب‌یابی، تعمیر و نگهداری اینورتر کولر.",
     "summary_en": "Troubleshooting, repair and maintenance of cooler inverters.",
     "body_fa": "تعمیر تخصصی اینورتر کولر شامل عیب‌یابی برد کنترل، موتور و سرویس دوره‌ای.",
     "body_en": "Specialist cooler inverter repair including control board and motor diagnostics plus periodic service.",
     "seo_title_fa": "تعمیر اینورتر کولر | الکتروگلد", "seo_title_en": "Cooler Inverter Repair | ElectroGold",
     "seo_description_fa": "عیب‌یابی و تعمیر اینورتر کولر با سرویس دوره‌ای و ضمانت.",
     "seo_description_en": "Cooler inverter troubleshooting and repair with periodic service and warranty.",
     "image_query": "air cooler conditioner repair technician"},
    {"slug": "solar-inverter-repair", "category": "solar",
     "title_fa": "تعمیر سانورتر خورشیدی", "title_en": "Solar Inverter Repair",
     "summary_fa": "عیب‌یابی و تعمیر سانورترهای گرووات.",
     "summary_en": "Troubleshooting and repair of Growatt solar inverters.",
     "body_fa": "تعمیر سانورتر خورشیدی گرووات شامل بررسی MPPT، برد قدرت و مانیتورینگ.",
     "body_en": "Growatt solar inverter repair including MPPT, power board and monitoring checks.",
     "seo_title_fa": "تعمیر سانورتر گرووات | الکتروگلد", "seo_title_en": "Growatt Solar Inverter Repair | ElectroGold",
     "seo_description_fa": "تعمیر و نگهداری سانورتر خورشیدی گرووات با عیب‌یابی دقیق.",
     "seo_description_en": "Growatt solar inverter repair and maintenance with precise diagnostics.",
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
     "image_query": "delta industrial drive panel", "services": ["industrial-inverter-repair"]},
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
]

ARTICLES = [
    {"slug": "elevator-inverter-fault-codes", "title_fa": "کدهای خطای اینورتر آسانسور", "title_en": "Elevator Inverter Fault Codes",
     "excerpt_fa": "راهنمای کدهای خطا و عیب‌یابی.", "excerpt_en": "Guide to fault codes and troubleshooting.",
     "body_fa": "در این مقاله کدهای خطای رایج بررسی می‌شود.", "body_en": "This article covers common fault codes.",
     "author": "ElectroGold", "seo_title_fa": "کدهای خطای اینورتر آسانسور | الکتروگلد",
     "seo_title_en": "Elevator Inverter Fault Codes | ElectroGold",
     "seo_description_fa": "راهنمای عیب‌یابی کدهای خطا.", "seo_description_en": "Fault code troubleshooting guide.",
     "image_query": "technician testing electrical panel"},
    {"slug": "industrial-vfd-maintenance", "title_fa": "نگهداری اینورتر صنعتی", "title_en": "Industrial VFD Maintenance",
     "excerpt_fa": "چک‌لیست نگهداری دوره‌ای درایو.", "excerpt_en": "Preventive maintenance checklist for drives.",
     "body_fa": "نگهداری پیشگیرانه طول عمر درایو را افزایش می‌دهد.", "body_en": "Preventive maintenance extends drive life.",
     "author": "ElectroGold", "seo_title_fa": "نگهداری اینورتر صنعتی | الکتروگلد",
     "seo_title_en": "Industrial VFD Maintenance | ElectroGold",
     "seo_description_fa": "چک‌لیست نگهداری اینورتر صنعتی.", "seo_description_en": "Industrial inverter maintenance checklist.",
     "image_query": "engineer maintaining industrial equipment"},
    {"slug": "growatt-solar-errors", "title_fa": "خطاهای رایج سانورتر گرووات", "title_en": "Common Growatt Solar Errors",
     "excerpt_fa": "رفع خطاهای سانورتر خورشیدی.", "excerpt_en": "Fixing solar inverter errors.",
     "body_fa": "خطاهای MPPT و اتصال به شبکه بررسی می‌شود.", "body_en": "MPPT and grid errors covered.",
     "author": "ElectroGold", "seo_title_fa": "خطاهای گرووات | الکتروگلد", "seo_title_en": "Growatt Errors | ElectroGold",
     "seo_description_fa": "رفع خطاهای سانورتر گرووات.", "seo_description_en": "Fixing Growatt inverter errors.",
     "image_query": "solar panels roof maintenance"},
    {"slug": "monarch-controller-guide", "title_fa": "راهنمای کنترلر مونارک", "title_en": "Monarch Controller Guide",
     "excerpt_fa": "تنظیم و عیب‌یابی مونارک.", "excerpt_en": "Monarch setup and troubleshooting.",
     "body_fa": "تنظیمات پایه کنترلر مونارک.", "body_en": "Basic Monarch controller setup.",
     "author": "ElectroGold", "seo_title_fa": "راهنمای مونارک | الکتروگلد", "seo_title_en": "Monarch Guide | ElectroGold",
     "seo_description_fa": "راهنمای کنترلر مونارک.", "seo_description_en": "Monarch controller guide.",
     "image_query": "elevator shaft control electronics", "services": ["elevator-inverter-repair"], "brands": ["monarch"]},
]

# The image service is best effort; these URLs keep every rendered card useful
# during an outage, and are supplied to find_images without entering a DB
# transaction.
for _record in SERVICES:
    _record["image_url"] = SERVICE_IMAGE_URLS[_record["slug"]]
    _record["focus_keyword_fa"] = _record["title_fa"]
    _record["focus_keyword_en"] = _record["title_en"].lower()
for _record in BRANDS:
    _record["image_url"] = BRAND_IMAGE_URL
for _record in ARTICLES:
    _record["image_url"] = ARTICLE_IMAGE_URL

SITE_SETTINGS = [
    {"language": "fa", "site_title": "الکتروگلد", "tagline": "عیب‌یابی، تعمیر و نگهداری اینورتر",
     "hero_title": "تعمیر تخصصی اینورتر آسانسور، صنعتی و سانورتر خورشیدی",
     "hero_subtitle": "عیب‌یابی در سطح قطعه، تست کامل زیر بار و گارانتی خدمات برای درایوهای یاسکاوا، مونارک، دلتا، اینوونس، اچ‌پی‌مونت، زیلابگ و سانورترهای گرووات.",
     "meta_description": "تعمیر تخصصی اینورتر آسانسور، اینورتر صنعتی و سانورتر خورشیدی در الکتروگلد؛ عیب‌یابی دقیق برد، تست زیر بار و گارانتی خدمات برای یاسکاوا، مونارک و دلتا.",
     "phone": "09120000000", "address": "تهران، ایران", "city": "تهران", "org_name": "الکتروگلد",
     "opening_hours_text": "شنبه تا پنجشنبه، ۸ تا ۱۸"},
    {"language": "en", "site_title": "ElectroGold", "tagline": "Inverter troubleshooting, repair & maintenance",
     "hero_title": "Specialist elevator, industrial and solar inverter repair",
     "hero_subtitle": "Component-level diagnostics, full load testing and a service warranty for Yaskawa, Monarch, Delta, Inovance, HPMont, Zilabeg drives and Growatt solar inverters.",
     "meta_description": "ElectroGold repairs elevator, industrial and solar inverters: component-level diagnostics, full load testing and warranty for Yaskawa, Monarch, Delta and Growatt.",
     "phone": "+989120000000", "address": "Tehran, Iran", "city": "Tehran", "org_name": "ElectroGold",
     "opening_hours_text": "Sat–Thu, 8:00–18:00"},
]

PAGE_SEO = [
    {"page": "home", "focus_keyword_fa": "تعمیر اینورتر", "focus_keyword_en": "inverter repair",
     "seo_title_fa": "تعمیر اینورتر آسانسور، صنعتی و خورشیدی | الکتروگلد",
     "seo_title_en": "Inverter Repair: Elevator, Industrial & Solar | ElectroGold"},
    {"page": "services", "focus_keyword_fa": "خدمات تعمیر اینورتر", "focus_keyword_en": "inverter repair services",
     "seo_title_fa": "خدمات تعمیر اینورتر و درایو | الکتروگلد",
     "seo_title_en": "Inverter & Drive Repair Services | ElectroGold",
     "seo_description_fa": "خدمات تعمیر اینورتر آسانسور، اینورتر صنعتی، دستگاه جوش، کولر و سانورتر خورشیدی؛ عیب‌یابی تخصصی، تست زیر بار و گارانتی در الکتروگلد.",
     "seo_description_en": "Inverter repair services for elevators, industrial drives, welding machines, coolers and solar inverters, with expert diagnostics, load testing and warranty.",
     "intro_fa": "عیب‌یابی، تعمیرات و نگهداری اینورترهای آسانسوری، صنعتی و خورشیدی.",
     "intro_en": "Troubleshooting, repair and maintenance of elevator, industrial and solar inverters."},
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
     "answer_fa": "اینورترهای آسانسوری یاسکاوا، مونارک، اچ‌پی‌مونت و زیلابگ، درایوهای صنعتی دلتا، یاسکاوا و اینوونس و سانورترهای خورشیدی گرووات.",
     "question_en": "Which inverter brands do you repair?",
     "answer_en": "Yaskawa, Monarch, HPMont and Zilabeg elevator drives; Delta, Yaskawa and Inovance industrial drives; and Growatt solar inverters."},
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
        for i, r in enumerate(SERVICES):
            self.upsert(Service, {"slug": r["slug"]}, {
                **self.fields(r, names), "image": self.image_for(images, r), "ordering": i,
                "schema_type": "Service"})
        Service.objects.exclude(slug__in=[r["slug"] for r in SERVICES]).update(published=False)

    def seed_brands(self, images):
        from apps.content.models import Brand, Service
        names = ("category", "name_fa", "name_en", "description_fa", "description_en", "content_fa", "content_en",
                 "seo_title_fa", "seo_title_en", "seo_description_fa", "seo_description_en")
        for i, r in enumerate(BRANDS):
            b = self.upsert(Brand, {"slug": r["slug"]}, {
                **self.fields(r, names), "logo": self.image_for(images, r), "ordering": i,
                "schema_type": "Brand"})
            if self.fresh or not b.services.exists():
                b.services.set(Service.objects.filter(slug__in=r.get("services", [])))
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
            if self.fresh or not (a.services.exists() or a.brands.exists()):
                a.services.set(Service.objects.filter(slug__in=r.get("services", [])))
                a.brands.set(Brand.objects.filter(slug__in=r.get("brands", [])))
        Article.objects.exclude(slug__in=[r["slug"] for r in ARTICLES]).update(published=False)

    def seed_seo(self):
        from apps.content.models import FaqItem, Service
        from apps.seo.models import GlobalSeoSetting, PageSeo, SiteSetting
        for r in SITE_SETTINGS:
            self.upsert(SiteSetting, {"language": r["language"]}, {k: v for k, v in r.items() if k != "language"})
        GlobalSeoSetting.load()
        self.upsert(GlobalSeoSetting, {"pk": 1}, {"org_schema_name": "ElectroGold"})
        for r in PAGE_SEO:
            self.upsert(PageSeo, {"page": r["page"]}, {k: v for k, v in r.items() if k != "page"})
        for i, r in enumerate(FAQS):
            service = Service.objects.filter(slug=r["service"]).first() if r.get("service") else None
            self.upsert(FaqItem, {"question_fa": r["question_fa"]}, {
                "answer_fa": r["answer_fa"], "question_en": r["question_en"], "answer_en": r["answer_en"],
                "show_on_home": r.get("home", False), "service": service, "ordering": i})

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

