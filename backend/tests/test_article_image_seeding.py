from unittest.mock import patch

from django.test import SimpleTestCase

from apps.common.management.commands.seed import ARTICLES, ARTICLE_SLUGS, Command


class ArticleImageSeedingTests(SimpleTestCase):
    def test_seeded_articles_use_topic_queries_instead_of_a_shared_photo(self):
        self.assertTrue(ARTICLE_SLUGS)
        for article in ARTICLES:
            with self.subTest(slug=article["slug"]):
                self.assertTrue(article.get("image_query"))
                self.assertNotIn("image_url", article)

    def test_article_search_results_are_unique_and_never_borrowed_from_fallback(self):
        command = Command()
        records = [
            {"slug": ARTICLES[0]["slug"], "image_query": "solar guide"},
            {"slug": ARTICLES[1]["slug"], "image_query": "drive guide"},
            {"slug": ARTICLES[2]["slug"], "image_query": "empty guide"},
        ]
        shared = {"url": "https://images.example/shared.jpg"}
        solar = {"url": "https://images.example/solar.jpg"}
        drive = {"url": "https://images.example/drive.jpg"}
        fallback = {"url": "https://images.example/generic.jpg"}

        def search(query):
            return {
                "solar guide": [shared, solar],
                "drive guide": [shared, drive],
                "empty guide": [],
                "industrial inverter repair technician": [fallback],
            }.get(query, [])

        with patch.object(command, "search", side_effect=search):
            images = command.find_images(records, "slug", refresh=False)

        self.assertEqual(images[ARTICLES[0]["slug"]]["url"], shared["url"])
        self.assertEqual(images[ARTICLES[1]["slug"]]["url"], drive["url"])
        self.assertNotIn(ARTICLES[2]["slug"], images)
        self.assertEqual(len({image["url"] for image in images.values()}), len(images))
