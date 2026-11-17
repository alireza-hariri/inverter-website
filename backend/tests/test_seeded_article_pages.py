import json
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from apps.common.management.commands.seed import BRAND_LOGO_PATHS
from apps.common.management.commands.delta_error_articles import DELTA_ERROR_ARTICLES
from apps.common.management.commands.elevator_service_content import ELEVATOR_SERVICE_BODY_FA
from apps.common.management.commands.industrial_service_content import INDUSTRIAL_SERVICE_BODY_FA
from apps.common.management.commands.solar_service_content import SOLAR_SERVICE_BODY_FA
from apps.common.management.commands.welding_service_content import WELDING_SERVICE_BODY_FA
from apps.common.management.commands.growatt_error_articles import GROWATT_ERROR_ARTICLES
from apps.common.management.commands.schneider_error_articles import SCHNEIDER_ERROR_ARTICLES
from apps.common.management.commands.siemens_error_articles import SIEMENS_ERROR_ARTICLES
from apps.common.management.commands.yaskawa_error_articles import YASKAWA_ERROR_ARTICLES
from apps.content.richtext import CTA_PLACEHOLDER
from apps.content.models import Article, Brand, Service


class SeededArticlePageTests(TestCase):
    def test_every_seeded_article_serializes_in_both_languages(self):
        Brand.objects.create(
            slug="shima", category="elevator", name_fa="شی ما", name_en="Shima",
            logo="/brands/shima.svg",
        )
        Brand.objects.create(
            slug="teta", category="elevator", name_fa="تتا", name_en="Teta",
            logo="/brands/teta.svg",
        )
        call_command("seed", "--no-demo", stdout=StringIO())

        articles = list(Article.objects.live())
        self.assertEqual(len(articles), 50)

        expected_services = [
            "elevator-inverter-repair",
            "industrial-inverter-repair",
            "solar-inverter-repair",
            "welding-inverter-repair",
            "automation-and-control-service",
        ]
        services = list(Service.objects.filter(published=True).order_by("ordering"))
        self.assertEqual([service.slug for service in services], expected_services)
        self.assertEqual(
            [service.title_fa for service in services],
            [
                "خدمات اینورتر آسانسور",
                "خدمات درایوهای صنعتی",
                "خدمات نیروگاه‌های خورشیدی/سانورتر",
                "خدمات تجهیزات جوشکاری",
                "خدمات اتوماسیون و کنترل",
            ],
        )
        service_listing = self.client.get("/api/services/", {"language": "fa", "page_size": 100})
        self.assertEqual(service_listing.status_code, 200)
        self.assertEqual(service_listing.json()["count"], 5)
        self.assertEqual([item["slug"] for item in service_listing.json()["results"]], expected_services)
        self.assertEqual(Brand.objects.filter(published=True).count(), len(BRAND_LOGO_PATHS))
        self.assertFalse(Brand.objects.get(slug="shima").published)
        self.assertEqual(self.client.get("/api/brands/shima/").status_code, 404)
        self.assertFalse(Brand.objects.get(slug="teta").published)
        self.assertEqual(self.client.get("/api/brands/teta/").status_code, 404)
        qma = Brand.objects.get(slug="kyuma")
        self.assertEqual((qma.name_fa, qma.name_en), ("QMA", "QMA"))
        self.assertEqual(
            self.client.get("/api/brands/kyuma/", {"language": "fa"}).json()["name"],
            "QMA",
        )
        self.assertEqual(
            self.client.get("/api/brands/kyuma/", {"language": "en"}).json()["name"],
            "QMA",
        )
        brand_faq = next(
            faq for faq in self.client.get("/api/content/home/", {"language": "fa"}).json()["faqs"]
            if faq["question"] == "اینورتر چه برندهایی را تعمیر می‌کنید؟"
        )
        self.assertIn("QMA", brand_faq["answer"])
        self.assertNotIn("کیوما", brand_faq["answer"])
        public_dir = Path(__file__).resolve().parents[2] / "frontend/public"
        for slug, logo_path in BRAND_LOGO_PATHS.items():
            self.assertEqual(Brand.objects.get(slug=slug).logo, logo_path)
            self.assertTrue((public_dir / logo_path.lstrip("/")).is_file(), logo_path)
        home = self.client.get("/api/content/home/", {"language": "fa"})
        self.assertEqual(home.status_code, 200)
        self.assertEqual({brand["slug"] for brand in home.json()["brands"]}, set(BRAND_LOGO_PATHS))
        self.assertTrue(all(brand["logo"].startswith("/brands/") for brand in home.json()["brands"]))
        elevator = Service.objects.get(slug="elevator-inverter-repair")
        self.assertEqual(elevator.body_fa, ELEVATOR_SERVICE_BODY_FA)
        industrial_service = Service.objects.get(slug="industrial-inverter-repair")
        self.assertEqual(industrial_service.body_fa, INDUSTRIAL_SERVICE_BODY_FA)
        solar_service = Service.objects.get(slug="solar-inverter-repair")
        self.assertEqual(solar_service.body_fa, SOLAR_SERVICE_BODY_FA)
        welding_service = Service.objects.get(slug="welding-inverter-repair")
        self.assertEqual(welding_service.body_fa, WELDING_SERVICE_BODY_FA)
        for service in services:
            for language in ("fa", "en"):
                with self.subTest(service=service.slug, language=language):
                    response = self.client.get(f"/api/services/{service.slug}/", {"language": language})
                    self.assertEqual(response.status_code, 200, response.content.decode())
                    self.assertTrue(response.json()["body_html"])
        elevator_detail = self.client.get("/api/services/elevator-inverter-repair/", {"language": "fa"}).json()
        self.assertIn("تعمیر تخصصی اینورتر آسانسور", elevator_detail["body_html"])
        self.assertIn('href="tel:09998703705"', elevator_detail["body_html"])
        elevator_brand_order = [
            "siemens", "delta", "yaskawa", "ls", "fuji", "danfoss", "abb", "invt", "sbt",
            "monarch", "kyuma", "hpmont", "zilabeg",
        ]
        self.assertEqual([brand["slug"] for brand in elevator_detail["related_brands"]], elevator_brand_order)
        self.assertSetEqual(
            {brand["slug"] for brand in elevator_detail["related_brands"]},
            set(elevator_brand_order),
        )
        self.assertTrue(all(brand["logo"].startswith("/brands/") for brand in elevator_detail["related_brands"]))
        industrial_detail = self.client.get("/api/services/industrial-inverter-repair/", {"language": "fa"}).json()
        self.assertIn("پایداری عملیاتی", industrial_detail["body_html"])
        solar_detail = self.client.get("/api/services/solar-inverter-repair/", {"language": "fa"}).json()
        self.assertEqual(
            [brand["slug"] for brand in solar_detail["related_brands"]],
            ["growatt", "solarx", "voltronic", "sma", "fronius", "huawei", "sungrow", "abb", "goodwe", "solis", "sofar", "must"],
        )
        welding_detail = self.client.get("/api/services/welding-inverter-repair/", {"language": "fa"}).json()
        self.assertEqual(
            [brand["slug"] for brand in welding_detail["related_brands"]],
            ["saba-electric", "iran-trans", "edon", "tosan", "fronius", "miller", "jasic", "arva"],
        )

        source_dir = Path(__file__).resolve().parents[1] / "apps/common/management/commands"
        imported_slugs = {"delta-inverter-ov-overvoltage-error-analysis"}
        for filename in (
            "delta_error_articles_source.json",
            "siemens_error_articles_source.json",
            "yaskawa_error_articles_source.json",
            "schneider_error_articles_source.json",
            "growatt_error_articles_source.json",
        ):
            records = json.loads((source_dir / filename).read_text(encoding="utf-8"))
            for slug, source in records.items():
                imported_slugs.add(slug)
                article = Article.objects.get(slug=slug)
                self.assertEqual(article.title_fa, source["title_fa"])
                self.assertEqual(article.body_fa, source["body_fa"])
        self.assertSetEqual({article.slug for article in articles}, imported_slugs)

        seeded_brands = (
            *DELTA_ERROR_ARTICLES,
            *SIEMENS_ERROR_ARTICLES,
            *YASKAWA_ERROR_ARTICLES,
            *SCHNEIDER_ERROR_ARTICLES,
            *GROWATT_ERROR_ARTICLES,
        )
        for record in seeded_brands:
            article = Article.objects.get(slug=record["slug"])
            self.assertSetEqual(set(article.services.values_list("slug", flat=True)), set(record["services"]))
            self.assertSetEqual(set(article.brands.values_list("slug", flat=True)), set(record["brands"]))

        for language in ("fa", "en"):
            listing = self.client.get("/api/articles/", {"language": language, "page_size": 100})
            self.assertEqual(listing.status_code, 200)
            self.assertEqual(listing.json()["count"], 50)
            self.assertEqual(len(listing.json()["results"]), 50)

        for article in articles:
            for language in ("fa", "en"):
                with self.subTest(slug=article.slug, language=language):
                    response = self.client.get(f"/api/articles/{article.slug}/", {"language": language})
                    self.assertEqual(response.status_code, 200, response.content.decode())
                    payload = response.json()
                    self.assertTrue(payload["title"])
                    self.assertTrue(payload["body_html"])
                    self.assertIsNone(CTA_PLACEHOLDER.search(payload["body_html"]))

            if CTA_PLACEHOLDER.search(article.body_fa):
                response = self.client.get(f"/api/articles/{article.slug}/", {"language": "fa"})
                body_html = response.json()["body_html"]
                self.assertTrue('href="tel:09998703705"' in body_html or 'href="/fa/contact"' in body_html)

        brand_article_slugs = {
            "delta": {"delta-inverter-ov-overvoltage-error-analysis", *(record["slug"] for record in DELTA_ERROR_ARTICLES)},
            "siemens": {record["slug"] for record in SIEMENS_ERROR_ARTICLES},
            "yaskawa": {record["slug"] for record in YASKAWA_ERROR_ARTICLES},
            "schneider": {record["slug"] for record in SCHNEIDER_ERROR_ARTICLES},
            "growatt": {record["slug"] for record in GROWATT_ERROR_ARTICLES},
        }
        for brand_slug, expected in brand_article_slugs.items():
            with self.subTest(brand=brand_slug):
                response = self.client.get(f"/api/brands/{brand_slug}/", {"language": "fa"})
                self.assertEqual(response.status_code, 200, response.content.decode())
                related = {article["slug"] for article in response.json()["related_articles"]}
                self.assertSetEqual(related, expected)

        industrial = Service.objects.get(slug="industrial-inverter-repair")
        industrial.title_fa = "عنوان قدیمی"
        industrial.summary_fa = "توضیح قدیمی"
        industrial.published = False
        industrial.ordering = 99
        industrial.save(update_fields=["title_fa", "summary_fa", "published", "ordering"])
        retired = Service.objects.create(
            slug="cooler-inverter-repair", category="industrial",
            title_fa="تعمیر اینورتر کولر", title_en="Cooler inverter repair",
        )
        call_command("seed", "--no-demo", stdout=StringIO())

        industrial.refresh_from_db()
        retired.refresh_from_db()
        self.assertEqual(industrial.title_fa, "خدمات درایوهای صنعتی")
        self.assertNotEqual(industrial.summary_fa, "توضیح قدیمی")
        self.assertTrue(industrial.published)
        self.assertEqual(industrial.ordering, 1)
        self.assertFalse(retired.published)
        self.assertEqual(Service.objects.filter(published=True).count(), 5)
