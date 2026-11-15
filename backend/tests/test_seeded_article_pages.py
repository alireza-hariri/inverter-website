import json
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from apps.common.management.commands.delta_error_articles import DELTA_ERROR_ARTICLES
from apps.common.management.commands.growatt_error_articles import GROWATT_ERROR_ARTICLES
from apps.common.management.commands.schneider_error_articles import SCHNEIDER_ERROR_ARTICLES
from apps.common.management.commands.siemens_error_articles import SIEMENS_ERROR_ARTICLES
from apps.common.management.commands.yaskawa_error_articles import YASKAWA_ERROR_ARTICLES
from apps.content.richtext import CTA_PLACEHOLDER
from apps.content.models import Article


class SeededArticlePageTests(TestCase):
    def test_every_seeded_article_serializes_in_both_languages(self):
        call_command("seed", "--no-demo", stdout=StringIO())

        articles = list(Article.objects.live())
        self.assertEqual(len(articles), 50)

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
                self.assertIn('href="tel:09998703705"', response.json()["body_html"])
