import json
from pathlib import Path

from django.test import SimpleTestCase

from apps.content.richtext import CTA_PLACEHOLDER, render


class RichTextCallToActionTests(SimpleTestCase):
    def test_docx_button_placeholder_becomes_a_call_link(self):
        placeholder = "[دکمه: مشاوره و ارسال درایو برای عیب‌یابی تخصصی اتصال زمین - تماس با الکتروگلد]"

        rendered, _ = render(f"<p>{placeholder}</p>", contact_phone="099 987 03705")

        self.assertIn('href="tel:09998703705"', rendered)
        self.assertIn("مشاوره و ارسال درایو برای عیب‌یابی تخصصی اتصال زمین", rendered)
        self.assertNotIn("[دکمه:", rendered)

    def test_plain_text_button_placeholder_is_rendered_as_a_call_link(self):
        rendered, _ = render("توضیح مقاله\n\n[دکمه: تماس با الکتروگلد]")

        self.assertIn('href="tel:09998703705"', rendered)
        self.assertIn("تماس با الکتروگلد", rendered)
        self.assertNotIn("[دکمه:", rendered)

    def test_schneider_button_variants_are_rendered_as_call_links(self):
        rendered, _ = render("[شماره تماس/دکمه تماس با کارشناسان الکتروگلد]")

        self.assertIn('href="tel:09998703705"', rendered)
        self.assertIn("تماس با کارشناسان الکتروگلد", rendered)
        self.assertIsNone(CTA_PLACEHOLDER.search(rendered))

    def test_plain_contact_call_to_action_is_rendered_as_a_button(self):
        rendered, _ = render("📞 همین حالا با کارشناسان الکتروگلد تماس بگیرید.")

        self.assertIn('href="tel:09998703705"', rendered)

    def test_site_visit_request_placeholder_links_to_the_contact_form(self):
        rendered, _ = render("[✉️ درخواست بازدید فنی و تست عملکرد سیستم]", contact_url="/fa/contact")

        self.assertIn('href="/fa/contact"', rendered)
        self.assertIn("درخواست بازدید فنی و تست عملکرد سیستم", rendered)
        self.assertIsNone(CTA_PLACEHOLDER.search(rendered))

    def test_form_link_placeholder_links_to_the_contact_form(self):
        rendered, _ = render("ارسال اطلاعات: از طریق [لینک واتس‌اپ/فرم] ارسال کنید.")

        self.assertIn('href="/fa/contact"', rendered)
        self.assertIn("لینک واتس‌اپ/فرم", rendered)
        self.assertIsNone(CTA_PLACEHOLDER.search(rendered))

    def test_placeholders_in_all_imported_brand_articles_become_call_links(self):
        command_dir = Path(__file__).resolve().parents[1] / "apps/common/management/commands"
        found = 0

        for source_path in command_dir.glob("*_error_articles_source.json"):
            articles = json.loads(source_path.read_text(encoding="utf-8"))
            for article in articles.values():
                placeholders = list(CTA_PLACEHOLDER.finditer(article["body_fa"]))
                if not placeholders:
                    continue
                found += len(placeholders)
                rendered, _ = render(article["body_fa"])
                self.assertIsNone(CTA_PLACEHOLDER.search(rendered))
                self.assertTrue(
                    'href="tel:09998703705"' in rendered or 'href="/fa/contact"' in rendered)

        self.assertGreater(found, 0)
