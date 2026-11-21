import json
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from apps.common.management.commands.seed import (
    BRAND_INTRO_COPY,
    BRAND_LOGO_PATHS,
    BRAND_PAGE_GUIDES,
    NON_ERROR_ARTICLE_SLUGS,
)
from apps.common.management.commands.delta_error_articles import DELTA_ERROR_ARTICLES
from apps.common.management.commands.elevator_service_content import ELEVATOR_SERVICE_BODY_FA
from apps.common.management.commands.industrial_service_content import INDUSTRIAL_SERVICE_BODY_FA
from apps.common.management.commands.solar_service_content import SOLAR_SERVICE_BODY_FA
from apps.common.management.commands.growatt_error_articles import GROWATT_ERROR_ARTICLES
from apps.common.management.commands.invt_error_articles import INVT_ERROR_ARTICLES
from apps.common.management.commands.solarx_error_articles import SOLARX_ERROR_ARTICLES
from apps.common.management.commands.comparison_articles import GENERAL_COMPARISON_ARTICLES
from apps.common.management.commands.schneider_error_articles import SCHNEIDER_ERROR_ARTICLES
from apps.common.management.commands.siemens_error_articles import SIEMENS_ERROR_ARTICLES
from apps.common.management.commands.yaskawa_error_articles import YASKAWA_ERROR_ARTICLES
from apps.content.richtext import CTA_PLACEHOLDER
from apps.content.models import Article, Brand, FaqItem, Service


class SeededArticlePageTests(TestCase):
    def test_seed_unpublishes_emergency_faq(self):
        faq = FaqItem.objects.create(
            question_fa="در خرابی اضطراری اینورتر چه اقدامی انجام دهم؟",
            question_en="What should I do if an inverter fails in an emergency?",
            answer_fa="پاسخ قدیمی",
            answer_en="Old answer",
            show_on_home=True,
            published=True,
        )

        call_command("seed", "--no-demo", stdout=StringIO())

        faq.refresh_from_db()
        self.assertFalse(faq.show_on_home)
        self.assertFalse(faq.published)

    def test_seed_moves_all_legacy_invt_articles_to_inovance(self):
        invt = Brand.objects.create(
            slug="invt", category="elevator", name_fa="اینوت", name_en="INVT",
        )
        manual_article = Article.objects.create(
            slug="manual-invt-article", title_fa="مقالهٔ INVT", title_en="INVT article",
        )
        manual_article.brands.add(invt)

        call_command("seed", "--no-demo", stdout=StringIO())

        manual_article.refresh_from_db()
        self.assertSetEqual(
            set(manual_article.brands.values_list("slug", flat=True)), {"inovance"}
        )
        self.assertFalse(Brand.objects.get(slug="invt").published)

    def test_every_seeded_article_serializes_in_both_languages(self):
        Brand.objects.create(
            slug="shima", category="elevator", name_fa="شی ما", name_en="Shima",
            logo="/brands/shima.svg",
        )
        Brand.objects.create(
            slug="teta", category="elevator", name_fa="تتا", name_en="Teta",
            logo="/brands/teta.svg",
        )
        Service.objects.create(
            slug="automation-and-control-service", category="industrial",
            title_fa="خدمات اتوماسیون و کنترل", title_en="Automation & Control Services",
        )
        retired_welding_service = Service.objects.create(
            slug="welding-inverter-repair", category="welding",
            title_fa="خدمات تجهیزات جوشکاری", title_en="Welding Equipment Services",
            published=True,
        )
        legacy_welding_brand = Brand.objects.create(
            slug="saba-electric", category="welding", name_fa="صبا الکتریک", name_en="Saba Electric",
            published=True,
        )
        legacy_welding_brand.services.add(retired_welding_service)
        legacy_fronius = Brand.objects.create(
            slug="fronius", category="welding", name_fa="فرونیوس", name_en="Fronius",
            published=True,
        )
        legacy_fronius.services.add(retired_welding_service)
        for slug in NON_ERROR_ARTICLE_SLUGS:
            Article.objects.create(slug=slug, title_fa=slug, title_en=slug)
        call_command("seed", "--no-demo", stdout=StringIO())

        articles = list(Article.objects.live())
        self.assertEqual(len(articles), 73)

        expected_services = [
            "elevator-inverter-repair",
            "industrial-inverter-repair",
            "solar-inverter-repair",
        ]
        services = list(Service.objects.filter(published=True).order_by("ordering"))
        self.assertEqual([service.slug for service in services], expected_services)
        self.assertEqual(
            [service.title_fa for service in services],
            [
                "خدمات اینورتر آسانسور",
                "خدمات درایوهای صنعتی",
                "خدمات نیروگاه‌های خورشیدی/سانورتر",
            ],
        )
        service_listing = self.client.get("/api/services/", {"language": "fa", "page_size": 100})
        self.assertEqual(service_listing.status_code, 200)
        self.assertEqual(service_listing.json()["count"], 3)
        self.assertEqual([item["slug"] for item in service_listing.json()["results"]], expected_services)
        retired_welding_service.refresh_from_db()
        self.assertFalse(retired_welding_service.published)
        self.assertEqual(
            self.client.get("/api/services/welding-inverter-repair/", {"language": "fa"}).status_code,
            404,
        )
        self.assertFalse(Brand.objects.get(slug="saba-electric").published)
        fronius = Brand.objects.get(slug="fronius")
        self.assertTrue(fronius.published)
        self.assertEqual(fronius.category, "solar")
        self.assertSetEqual(
            set(fronius.services.values_list("slug", flat=True)), {"solar-inverter-repair"}
        )
        fronius_detail = self.client.get("/api/brands/fronius/", {"language": "fa"}).json()
        self.assertEqual(
            [service["slug"] for service in fronius_detail["related_services"]],
            ["solar-inverter-repair"],
        )
        self.assertFalse(Service.objects.get(slug="automation-and-control-service").published)
        self.assertEqual(
            self.client.get("/api/services/automation-and-control-service/", {"language": "fa"}).status_code,
            404,
        )
        self.assertEqual(Brand.objects.filter(published=True).count(), len(BRAND_LOGO_PATHS))
        self.assertSetEqual(set(BRAND_INTRO_COPY), set(BRAND_LOGO_PATHS))
        for brand in Brand.objects.filter(published=True):
            with self.subTest(brand=brand.slug):
                self.assertTrue(brand.description_fa)
                self.assertTrue(brand.description_en)
                self.assertTrue(brand.content_fa)
                self.assertTrue(brand.content_en)
                self.assertLessEqual(len(brand.description_fa), 140)
                self.assertLessEqual(len(brand.description_en), 120)
                content_limit = 8000 if brand.slug in BRAND_PAGE_GUIDES else 1500
                self.assertLessEqual(len(brand.content_fa), content_limit)
                self.assertLessEqual(len(brand.content_en), content_limit)
                self.assertGreaterEqual(len(brand.content_fa), 300)
                self.assertGreaterEqual(len(brand.content_en), 300)
                self.assertTrue(
                    brand.name_fa in brand.content_fa or brand.name_en in brand.content_fa,
                    f"Persian brand intro should identify {brand.slug}",
                )
                self.assertIn(brand.name_en, brand.content_en)
        self.assertFalse(Brand.objects.get(slug="shima").published)
        self.assertEqual(self.client.get("/api/brands/shima/").status_code, 404)
        self.assertFalse(Brand.objects.get(slug="teta").published)
        self.assertEqual(self.client.get("/api/brands/teta/").status_code, 404)
        self.assertEqual(self.client.get("/api/brands/invt/").status_code, 404)
        self.assertFalse(Brand.objects.filter(slug="invt", published=True).exists())
        inovance = self.client.get("/api/brands/inovance/", {"language": "fa"}).json()
        self.assertSetEqual(set(inovance["categories"]), {"elevator", "industrial"})
        self.assertFalse(Article.objects.filter(slug__in=NON_ERROR_ARTICLE_SLUGS).exists())
        self.assertEqual(self.client.get("/api/articles/elevator-inverter-fault-codes/").status_code, 404)
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
        self.assertEqual(len(INVT_ERROR_ARTICLES), 10)
        self.assertEqual(len(SOLARX_ERROR_ARTICLES), 10)
        self.assertEqual(len(GENERAL_COMPARISON_ARTICLES), 3)
        brand_faq = next(
            faq for faq in self.client.get("/api/content/home/", {"language": "fa"}).json()["faqs"]
            if faq["question"] == "چه برندهایی را تعمیر می‌کنید؟"
        )
        self.assertIn("QMA", brand_faq["answer"])
        self.assertNotIn("کیوما", brand_faq["answer"])
        self.assertNotIn("جوشکاری", brand_faq["answer"])
        english_brand_faq = next(
            faq for faq in self.client.get("/api/content/home/", {"language": "en"}).json()["faqs"]
            if faq["question"] == "Which brands do you repair?"
        )
        self.assertNotIn("welding", english_brand_faq["answer"].lower())
        home_faqs = self.client.get("/api/content/home/", {"language": "fa"}).json()["faqs"]
        self.assertEqual(
            [faq["question"] for faq in home_faqs],
            [
                "هزینه بررسی و تعمیر اینورتر و درایو چقدر است؟",
                "عیب‌یابی و تعمیر اینورتر و درایو چقدر زمان می‌برد؟",
                "آیا تعمیر دستگاه شامل گارانتی می‌شود؟",
                "تعمیر دستگاه در محل انجام می‌شود یا باید به کارگاه الکتروگلد ارسال شود؟",
                "چه برندهایی را تعمیر می‌کنید؟",
                "چطور می‌توانم دستگاه را برای تعمیر به الکتروگلد تحویل بدهم؟",
                "برای بررسی دستگاه چه اطلاعاتی بفرستم؟",
            ],
        )
        self.assertNotIn(
            "در خرابی اضطراری اینورتر چه اقدامی انجام دهم؟",
            [faq["question"] for faq in home_faqs],
        )
        answers_by_question = {faq["question"]: faq["answer"] for faq in home_faqs}
        time_answer = answers_by_question["عیب‌یابی و تعمیر اینورتر و درایو چقدر زمان می‌برد؟"]
        self.assertIn("در همان روز اعلام می‌شود", time_answer)
        self.assertIn("آماده‌شدن دستگاه در همان روز نیست", time_answer)
        warranty_answer = answers_by_question["آیا تعمیر دستگاه شامل گارانتی می‌شود؟"]
        self.assertIn("گارانتی کتبی", warranty_answer)
        self.assertIn("مدت و شرایط گارانتی", warranty_answer)
        onsite_answer = answers_by_question[
            "تعمیر دستگاه در محل انجام می‌شود یا باید به کارگاه الکتروگلد ارسال شود؟"
        ]
        self.assertIn("در محل شما", onsite_answer)
        self.assertIn("در کارگاه الکتروگلد", onsite_answer)
        brand_answer = answers_by_question["چه برندهایی را تعمیر می‌کنید؟"]
        self.assertIn("ZIEHL-ABEGG", brand_answer)
        self.assertNotIn("Zilla", brand_answer)
        self.assertIn("اینورترهای خورشیدی:", brand_answer)
        delivery_answer = answers_by_question[
            "چطور می‌توانم دستگاه را برای تعمیر به الکتروگلد تحویل بدهم؟"
        ]
        self.assertIn("حضوری تحویل دهید", delivery_answer)
        self.assertIn("برای تحویل‌گرفتن آن به محل شما بیاییم", delivery_answer)
        self.assertIn("هزینهٔ احتمالی", delivery_answer)
        information_answer = answers_by_question["برای بررسی دستگاه چه اطلاعاتی بفرستم؟"]
        self.assertIn("عکس واضح از پلاک مشخصات", information_answer)
        self.assertIn("کد خطا", information_answer)
        self.assertIn("لازم نیست همهٔ این موارد را داشته باشید", information_answer)
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
        for service in services:
            for language in ("fa", "en"):
                with self.subTest(service=service.slug, language=language):
                    response = self.client.get(f"/api/services/{service.slug}/", {"language": language})
                    self.assertEqual(response.status_code, 200, response.content.decode())
                    self.assertTrue(response.json()["body_html"])
        elevator_detail = self.client.get("/api/services/elevator-inverter-repair/", {"language": "fa"}).json()
        self.assertIn("تعمیر تخصصی اینورتر آسانسور", elevator_detail["body_html"])
        self.assertIn('href="tel:02140228578"', elevator_detail["body_html"])
        elevator_brand_order = [
            "siemens", "delta", "yaskawa", "ls", "fuji", "danfoss", "abb", "inovance", "sbt",
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
        self.assertFalse(
            {"saba-electric", "iran-trans", "edon", "tosan", "miller", "jasic", "arva"}
            & set(BRAND_LOGO_PATHS)
        )

        source_dir = Path(__file__).resolve().parents[1] / "apps/common/management/commands"
        imported_slugs = {"delta-inverter-ov-overvoltage-error-analysis"}
        invt_article_bodies = {record["slug"]: record["body_fa"] for record in INVT_ERROR_ARTICLES}
        solarx_article_bodies = {record["slug"]: record["body_fa"] for record in SOLARX_ERROR_ARTICLES}
        comparison_article_bodies = {record["slug"]: record["body_fa"] for record in GENERAL_COMPARISON_ARTICLES}
        for filename in (
            "delta_error_articles_source.json",
            "siemens_error_articles_source.json",
            "yaskawa_error_articles_source.json",
            "schneider_error_articles_source.json",
            "growatt_error_articles_source.json",
            "invt_error_articles_source.json",
            "solarx_error_articles_source.json",
            "comparison_articles_source.json",
        ):
            records = json.loads((source_dir / filename).read_text(encoding="utf-8"))
            for slug, source in records.items():
                imported_slugs.add(slug)
                article = Article.objects.get(slug=slug)
                self.assertEqual(article.title_fa, source["title_fa"])
                expected_body = invt_article_bodies.get(
                    slug,
                    solarx_article_bodies.get(
                        slug, comparison_article_bodies.get(slug, source["body_fa"])
                    ),
                )
                self.assertEqual(article.body_fa, expected_body)
        self.assertSetEqual({article.slug for article in articles}, imported_slugs)

        seeded_brands = (
            *DELTA_ERROR_ARTICLES,
            *SIEMENS_ERROR_ARTICLES,
            *YASKAWA_ERROR_ARTICLES,
            *SCHNEIDER_ERROR_ARTICLES,
            *GROWATT_ERROR_ARTICLES,
            *INVT_ERROR_ARTICLES,
            *SOLARX_ERROR_ARTICLES,
            *GENERAL_COMPARISON_ARTICLES,
        )
        for record in seeded_brands:
            article = Article.objects.get(slug=record["slug"])
            self.assertSetEqual(set(article.services.values_list("slug", flat=True)), set(record["services"]))
            expected_brands = {
                resolved_slug
                for source_slug in record["brands"]
                for resolved_slug in ["inovance" if source_slug == "invt" else source_slug]
                if Brand.objects.filter(slug=resolved_slug, published=True).exists()
            }
            self.assertSetEqual(set(article.brands.values_list("slug", flat=True)), expected_brands)

        for language in ("fa", "en"):
            listing = self.client.get("/api/articles/", {"language": language, "page_size": 100})
            self.assertEqual(listing.status_code, 200)
            self.assertEqual(listing.json()["count"], 73)
            self.assertEqual(len(listing.json()["results"]), 73)
            article_images = [item["image"] for item in listing.json()["results"]]
            self.assertEqual(len(set(article_images)), 73)
            self.assertTrue(all(image.startswith("/articles/") for image in article_images))
            self.assertEqual(sum(item["article_type"] == "brand_specific" for item in listing.json()["results"]), 70)
            self.assertEqual(sum(item["article_type"] == "general" for item in listing.json()["results"]), 3)
            general_listing = self.client.get(
                "/api/articles/", {"language": language, "article_type": "general", "page_size": 100}
            )
            self.assertEqual(general_listing.status_code, 200)
            self.assertEqual(general_listing.json()["count"], 3)
            brand_listing = self.client.get(
                "/api/articles/", {"language": language, "article_type": "brand_specific", "page_size": 100}
            )
            self.assertEqual(brand_listing.status_code, 200)
            self.assertEqual(brand_listing.json()["count"], 70)

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
                self.assertTrue('href="tel:02140228578"' in body_html or 'href="/fa/contact"' in body_html)

        brand_article_slugs = {
            "delta": {"delta-inverter-ov-overvoltage-error-analysis", "delta-vs-invt-industrial-drive-comparison", *(record["slug"] for record in DELTA_ERROR_ARTICLES)},
            "siemens": {"siemens-sinamics-vs-abb-acs-comparison", *(record["slug"] for record in SIEMENS_ERROR_ARTICLES)},
            "yaskawa": {record["slug"] for record in YASKAWA_ERROR_ARTICLES},
            "schneider": {record["slug"] for record in SCHNEIDER_ERROR_ARTICLES},
            "growatt": {record["slug"] for record in GROWATT_ERROR_ARTICLES},
            "inovance": {"delta-vs-invt-industrial-drive-comparison", *(record["slug"] for record in INVT_ERROR_ARTICLES)},
            "solarx": {record["slug"] for record in SOLARX_ERROR_ARTICLES},
            "abb": {"siemens-sinamics-vs-abb-acs-comparison"},
            "huawei": {"huawei-vs-sungrow-solar-inverter-comparison"},
            "sungrow": {"huawei-vs-sungrow-solar-inverter-comparison"},
        }
        for brand_slug, expected in brand_article_slugs.items():
            with self.subTest(brand=brand_slug):
                response = self.client.get(f"/api/brands/{brand_slug}/", {"language": "fa"})
                self.assertEqual(response.status_code, 200, response.content.decode())
                related = {article["slug"] for article in response.json()["related_articles"]}
                self.assertSetEqual(related, expected)
                if brand_slug in {"delta", "siemens", "abb", "huawei", "sungrow"}:
                    related_types = {
                        article["slug"]: article["article_type"]
                        for article in response.json()["related_articles"]
                    }
                    for comparison in GENERAL_COMPARISON_ARTICLES:
                        if brand_slug in comparison["brands"]:
                            self.assertEqual(related_types[comparison["slug"]], "general")

        workbook_guide_checks = {
            "siemens": ("SINAMICS V20", "F0022", "../articles/siemens-drive-f0001-instantaneous-overcurrent"),
            "delta": ("VFD-VL", "LV · افت ولتاژ", "../articles/delta-inverter-ov-overvoltage-error-analysis"),
            "schneider": ("Altivar 320 (ATV320)", "InF · خطای داخلی", "../articles/schneider-drive-ocf"),
            "inovance": ("Goodrive 350 (GD350)", "OUT1 / OUT2 / OUT3", "../articles/invt-drive-communication-error"),
        }
        for brand_slug, markers in workbook_guide_checks.items():
            with self.subTest(workbook_guide=brand_slug):
                detail = self.client.get(f"/api/brands/{brand_slug}/", {"language": "fa"}).json()
                for marker in markers:
                    self.assertIn(marker, detail["content_html"])
                english_detail = self.client.get(f"/api/brands/{brand_slug}/", {"language": "en"}).json()
                self.assertIn("Read guide", english_detail["content_html"])
                self.assertNotIn("مقالهٔ مرتبط", english_detail["content_html"])

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
        self.assertEqual(Service.objects.filter(published=True).count(), 3)

    def test_general_comparison_can_link_to_both_brands(self):
        call_command("seed", "--no-demo", stdout=StringIO())
        comparison_slugs = {record["slug"] for record in GENERAL_COMPARISON_ARTICLES}

        for language in ("fa", "en"):
            general_listing = self.client.get(
                "/api/articles/", {"language": language, "article_type": "general", "page_size": 100}
            )
            self.assertEqual(general_listing.status_code, 200)
            self.assertEqual(general_listing.json()["count"], 3)
            self.assertSetEqual(
                {item["slug"] for item in general_listing.json()["results"]}, comparison_slugs
            )

        for brand_slug, expected_slug in (
            ("huawei", "huawei-vs-sungrow-solar-inverter-comparison"),
            ("sungrow", "huawei-vs-sungrow-solar-inverter-comparison"),
            ("siemens", "siemens-sinamics-vs-abb-acs-comparison"),
            ("abb", "siemens-sinamics-vs-abb-acs-comparison"),
            ("delta", "delta-vs-invt-industrial-drive-comparison"),
            ("inovance", "delta-vs-invt-industrial-drive-comparison"),
        ):
            with self.subTest(brand=brand_slug):
                detail = self.client.get(f"/api/brands/{brand_slug}/", {"language": "fa"}).json()
                linked = next(a for a in detail["related_articles"] if a["slug"] == expected_slug)
                self.assertEqual(linked["article_type"], "general")
