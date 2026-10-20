from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.content.models import Article, FaqItem, Service
from apps.content.richtext import render
from apps.seo import analysis
from apps.seo.models import NotFoundLog, PageSeo, Redirect


class RichTextTests(TestCase):
    def test_strips_scripts_and_handlers(self):
        html, _ = render('<p onclick="x()">hi<script>alert(1)</script><img src="a.jpg" onerror="x()"></p>')
        self.assertNotIn("script", html)
        self.assertNotIn("onclick", html)
        self.assertNotIn("onerror", html)

    def test_plain_text_becomes_paragraphs(self):
        html, _ = render("one\ntwo\n\nthree & <four")
        self.assertEqual(html, "<p>one<br>two</p><p>three &amp; &lt;four</p>")

    def test_headings_get_ids_and_toc(self):
        html, toc = render("<h2>Fault codes</h2><p>x</p><h2>Fault codes</h2><h3>عیب‌یابی</h3>")
        self.assertEqual([t["id"] for t in toc], ["fault-codes", "fault-codes-2", toc[2]["id"]])
        self.assertIn('<h2 id="fault-codes">', html)
        self.assertEqual(toc[2]["level"], 3)

    def test_only_external_links_get_rel(self):
        html, _ = render('<p><a href="/fa/brands">in</a><a href="https://x.com">out</a></p>')
        self.assertIn('<a href="/fa/brands">', html)
        self.assertIn('href="https://x.com" rel="noopener"', html)


class RedirectModelTests(TestCase):
    def test_paths_are_normalised(self):
        r = Redirect(old_path="fa/old/", new_path="/fa/new/", status_code=301)
        r.full_clean()
        self.assertEqual((r.old_path, r.new_path), ("/fa/old", "/fa/new"))

    def test_self_redirect_rejected(self):
        with self.assertRaises(ValidationError):
            Redirect(old_path="/fa/a", new_path="/fa/a/").full_clean()

    def test_loop_rejected(self):
        Redirect.objects.create(old_path="/fa/b", new_path="/fa/a")
        with self.assertRaises(ValidationError):
            Redirect(old_path="/fa/a", new_path="/fa/b").full_clean()

    def test_410_needs_no_target(self):
        Redirect(old_path="/fa/gone", new_path="", status_code=410).full_clean()


class SeoApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_settings_include_all_pages(self):
        body = self.client.get("/api/seo/settings/?language=fa").json()
        self.assertEqual(set(body["pages"]), {"home", "services", "brands", "articles", "about", "contact"})
        self.assertIn("verification", body["global"])

    def test_redirects_list_only_active(self):
        Redirect.objects.create(old_path="/fa/x", new_path="/fa/y")
        Redirect.objects.create(old_path="/fa/z", new_path="/fa/y", active=False)
        self.assertEqual([r["old_path"] for r in self.client.get("/api/seo/redirects/").json()["results"]], ["/fa/x"])

    def test_sitemap_skips_scheduled_noindex_and_hidden_pages(self):
        now = timezone.now()
        Article.objects.create(slug="live", title_fa="a", title_en="a", published_at=now - timedelta(days=1))
        Article.objects.create(slug="later", title_fa="b", title_en="b", published_at=now + timedelta(days=1))
        Article.objects.create(slug="hidden", title_fa="c", title_en="c", no_index=True)
        PageSeo.objects.filter(page="about").update(no_index=True)
        records = self.client.get("/api/seo/sitemap/?language=fa").json()["results"]
        slugs = {r["slug"] for r in records if r["route"] == "article"}
        self.assertEqual(slugs, {"live"})
        self.assertNotIn("about", {r["route"] for r in records})

    def test_scheduled_article_is_not_found(self):
        Article.objects.create(slug="later", title_fa="b", title_en="b", published_at=timezone.now() + timedelta(days=1))
        self.assertEqual(self.client.get("/api/articles/later/?language=fa").status_code, 404)

    @override_settings(SEO_INGEST_TOKEN="secret")
    def test_not_found_report_needs_token_and_counts_hits(self):
        self.assertEqual(self.client.post("/api/seo/not-found/", {"path": "/fa/x"}, format="json").status_code, 403)
        for _ in range(2):
            res = self.client.post("/api/seo/not-found/", {"path": "/fa/x/?a=1"}, format="json", HTTP_X_SEO_TOKEN="secret")
            self.assertEqual(res.status_code, 204)
        self.assertEqual(NotFoundLog.objects.get(path="/fa/x").hits, 2)

    @override_settings(SEO_INGEST_TOKEN="", DEBUG=False)
    def test_not_found_report_disabled_without_token_in_production(self):
        self.assertEqual(self.client.post("/api/seo/not-found/", {"path": "/fa/x"}, format="json").status_code, 403)

    def test_service_detail_has_html_and_faqs(self):
        s = Service.objects.create(slug="s", category="solar", title_fa="t", title_en="t", body_fa="<h2>H</h2>")
        FaqItem.objects.create(service=s, question_fa="q?", answer_fa="a.")
        body = self.client.get("/api/services/s/?language=fa").json()
        self.assertEqual(body["body_html"], '<h2 id="h">H</h2>')
        self.assertEqual(body["faqs"], [{"question": "q?", "answer": "a."}])
        # Untranslated FAQs are left off the English page rather than shown blank.
        self.assertEqual(self.client.get("/api/services/s/?language=en").json()["faqs"], [])


class AnalysisTests(TestCase):
    def test_missing_keyphrase_is_poor(self):
        s = Service(slug="s", title_fa="تعمیر", body_fa="")
        self.assertEqual(analysis.score(analysis.analyse(s, "fa")), "bad")

    def test_well_optimised_page_is_good(self):
        kw = "تعمیر اینورتر"
        body = "<h2>عنوان</h2><p>" + (f"{kw} " + "کلمه " * 60) * 6 + '<a href="/fa/brands">x</a></p>'
        s = Service(slug="s", title_fa=kw, summary_fa=f"{kw} سریع", body_fa=body, focus_keyword_fa=kw,
                    seo_title_fa=f"{kw} آسانسور و صنعتی | الکتروگلد",
                    seo_description_fa=f"{kw} " + "توضیح " * 22, image="x.jpg", image_alt_fa="alt")
        self.assertEqual(analysis.score(analysis.analyse(s, "fa")), "good")
