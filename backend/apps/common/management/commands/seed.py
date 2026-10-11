
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
for _record in BRANDS:
    _record["image_url"] = BRAND_IMAGE_URL
for _record in ARTICLES:
    _record["image_url"] = ARTICLE_IMAGE_URL

SITE_SETTINGS = [
    {"language": "fa", "site_title": "الکتروگلد", "tagline": "عیب‌یابی، تعمیر و نگهداری اینورتر",
     "meta_description": "الکتروگلد: تعمیر تخصصی اینورتر آسانسور، صنعتی و سانورتر خورشیدی.",
     "phone": "09120000000", "address": "تهران، ایران", "org_name": "الکتروگلد"},
    {"language": "en", "site_title": "ElectroGold", "tagline": "Inverter troubleshooting, repair & maintenance",
     "meta_description": "ElectroGold: elevator, industrial and solar inverter repair specialists.",
     "phone": "+989120000000", "address": "Tehran, Iran", "org_name": "ElectroGold"},
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

    def seed_services(self, images):
        from django.utils import timezone
        from apps.content.models import Service
        for i, r in enumerate(SERVICES):
            img = images.get(r["slug"], {}).get("url", "") if isinstance(images.get(r["slug"]), dict) else (images.get(r["slug"], "") or "")
            existing_image = Service.objects.filter(slug=r["slug"]).values_list("image", flat=True).first() or ""
            service, _ = Service.objects.update_or_create(slug=r["slug"], defaults={
                "category": r["category"], "title_fa": r["title_fa"], "title_en": r["title_en"],
                "summary_fa": r["summary_fa"], "summary_en": r["summary_en"],
                "body_fa": r["body_fa"], "body_en": r["body_en"],
                "seo_title_fa": r["seo_title_fa"], "seo_title_en": r["seo_title_en"],
                "seo_description_fa": r["seo_description_fa"], "seo_description_en": r["seo_description_en"],
                "image": img or existing_image or r.get("image_url", ""), "published": True, "ordering": i})
        Service.objects.exclude(slug__in=[r["slug"] for r in SERVICES]).update(published=False)

    def seed_brands(self, images):
        from apps.content.models import Brand, Service
        for i, r in enumerate(BRANDS):
            img = images.get(r["slug"], {}).get("url", "") if isinstance(images.get(r["slug"]), dict) else (images.get(r["slug"], "") or "")
            existing_logo = Brand.objects.filter(slug=r["slug"]).values_list("logo", flat=True).first() or ""
            b, _ = Brand.objects.update_or_create(slug=r["slug"], defaults={
                "category": r["category"], "name_fa": r["name_fa"], "name_en": r["name_en"],
                "description_fa": r["description_fa"], "description_en": r["description_en"],
                "content_fa": r["content_fa"], "content_en": r["content_en"],
                "seo_title_fa": r["seo_title_fa"], "seo_title_en": r["seo_title_en"],
                "seo_description_fa": r["seo_description_fa"], "seo_description_en": r["seo_description_en"],
                "logo": img or existing_logo or r.get("image_url", ""), "published": True, "ordering": i})
            b.services.set(Service.objects.filter(slug__in=r.get("services", [])))
        Brand.objects.exclude(slug__in=[r["slug"] for r in BRANDS]).update(published=False)

    def seed_articles(self, images):
        from django.utils import timezone
        from datetime import timedelta
        from apps.content.models import Article, Brand, Service
        for i, r in enumerate(ARTICLES):
            img = images.get(r["slug"], {}).get("url", "") if isinstance(images.get(r["slug"]), dict) else (images.get(r["slug"], "") or "")
            existing_image = Article.objects.filter(slug=r["slug"]).values_list("image", flat=True).first() or ""
            a, _ = Article.objects.update_or_create(slug=r["slug"], defaults={
                "title_fa": r["title_fa"], "title_en": r["title_en"],
                "excerpt_fa": r["excerpt_fa"], "excerpt_en": r["excerpt_en"],
                "body_fa": r["body_fa"], "body_en": r["body_en"],
                "author": r.get("author", ""), "image": img, "published": True,
                "published_at": timezone.now() - timedelta(days=i),
                "seo_title_fa": r["seo_title_fa"], "seo_title_en": r["seo_title_en"],
                "seo_description_fa": r["seo_description_fa"], "seo_description_en": r["seo_description_en"],
                "image": img or existing_image or r.get("image_url", "")})
            a.services.set(Service.objects.filter(slug__in=r.get("services", [])))
            a.brands.set(Brand.objects.filter(slug__in=r.get("brands", [])))
        Article.objects.exclude(slug__in=[r["slug"] for r in ARTICLES]).update(published=False)

    def seed_seo(self):
        from apps.seo.models import GlobalSeoSetting, SiteSetting
        for r in SITE_SETTINGS:
            SiteSetting.objects.update_or_create(language=r["language"], defaults={k: v for k, v in r.items() if k != "language"})
        GlobalSeoSetting.objects.get_or_create(pk=1, defaults={"canonical_host": "", "org_schema_name": "ElectroGold", "org_schema_url": ""})

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

