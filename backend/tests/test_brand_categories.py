from django.test import TestCase

from apps.content.models import Brand, Service


class BrandCategoryTests(TestCase):
    def setUp(self):
        self.elevator = Service.objects.create(
            slug="elevator-service", category="elevator", title_fa="آسانسور", title_en="Elevator",
        )
        self.industrial = Service.objects.create(
            slug="industrial-service", category="industrial", title_fa="صنعتی", title_en="Industrial",
        )
        self.solar = Service.objects.create(
            slug="solar-service", category="solar", title_fa="خورشیدی", title_en="Solar",
        )
        self.welding = Service.objects.create(
            slug="welding-service", category="welding", title_fa="جوشکاری", title_en="Welding",
        )
        self.multi_category = Brand.objects.create(
            slug="multi-category", category="elevator", name_fa="چنددسته", name_en="Multi-category",
        )
        self.multi_category.services.add(self.elevator, self.solar, self.industrial, self.welding)
        self.single_category = Brand.objects.create(
            slug="single-category", category="industrial", name_fa="تک‌دسته", name_en="Single-category",
        )
        self.single_category.services.add(self.industrial)
        Brand.objects.create(
            slug="legacy-category", category="solar", name_fa="قدیمی", name_en="Legacy",
        )
        self.welding_only = Brand.objects.create(
            slug="welding-only", category="welding", name_fa="جوشکاری", name_en="Welding-only",
        )
        self.welding_only.services.add(self.welding)

    def test_brand_categories_come_from_published_related_services(self):
        response = self.client.get("/api/brands/", {"page_size": 50})

        self.assertEqual(response.status_code, 200)
        results = {item["slug"]: item for item in response.json()["results"]}
        self.assertEqual(results["multi-category"]["categories"], ["elevator", "solar", "industrial", "welding"])
        self.assertEqual(results["single-category"]["categories"], ["industrial"])
        self.assertEqual(results["legacy-category"]["categories"], ["solar"])
        self.assertEqual(results["welding-only"]["categories"], ["welding"])

    def test_category_filter_includes_multi_category_brands(self):
        elevator = self.client.get("/api/brands/", {"category": "elevator", "page_size": 50})
        industrial = self.client.get("/api/brands/", {"category": "industrial", "page_size": 50})
        solar = self.client.get("/api/brands/", {"category": "solar", "page_size": 50})
        welding = self.client.get("/api/brands/", {"category": "welding", "page_size": 50})

        self.assertEqual({item["slug"] for item in elevator.json()["results"]}, {"multi-category"})
        self.assertEqual(
            {item["slug"] for item in industrial.json()["results"]},
            {"multi-category", "single-category"},
        )
        self.assertEqual({item["slug"] for item in solar.json()["results"]}, {"legacy-category", "multi-category"})
        self.assertEqual({item["slug"] for item in welding.json()["results"]}, {"multi-category", "welding-only"})

    def test_unpublished_services_do_not_add_a_brand_category(self):
        hidden_service = Service.objects.create(
            slug="hidden-solar-service", category="solar", title_fa="خورشیدی", title_en="Solar",
            published=False,
        )
        self.single_category.services.add(hidden_service)

        response = self.client.get("/api/brands/single-category/")

        self.assertEqual(response.json()["categories"], ["industrial"])
