import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.content.backups import create_backup, restore_backup
from apps.content.models import Article, Brand, FaqItem, Service
from apps.inquiries.models import ContactInquiry


class ContentBackupTests(TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.enterContext(self.settings(CONTENT_EXPORT_DIR=Path(self.temp_dir.name)))

    def tearDown(self):
        self.temp_dir.cleanup()

    def make_content(self):
        service = Service.objects.create(
            slug="inverter-repair", category="industrial", title_fa="تعمیر اینورتر",
            title_en="Inverter repair", summary_fa="خلاصه", body_fa="متن خدمات",
        )
        brand = Brand.objects.create(
            slug="example-brand", category="industrial", name_fa="برند نمونه",
            name_en="Example brand", content_fa="درباره برند",
        )
        brand.services.add(service)
        article = Article.objects.create(
            slug="repair-guide", title_fa="راهنمای تعمیر", title_en="Repair guide",
            body_fa="متن مقاله", author="نویسنده",
        )
        article.services.add(service)
        article.brands.add(brand)
        faq = FaqItem.objects.create(
            question_fa="پرسش؟", answer_fa="پاسخ", article=article, published=True,
        )
        return service, brand, article, faq

    def test_export_and_restore_content_records_and_relations(self):
        service, brand, article, faq = self.make_content()
        ContactInquiry.objects.create(name="Customer", mobile="09123456789", message="Private request")

        backup = create_backup()
        payload = json.loads(backup.read_text(encoding="utf-8"))
        self.assertEqual(backup.parent, Path(self.temp_dir.name))
        self.assertEqual(payload["format"], "electrogold-content-backup")
        self.assertEqual(len(payload["records"]), 4)
        self.assertEqual({record["model"] for record in payload["records"]}, {
            "content.service", "content.brand", "content.article", "content.faqitem",
        })

        FaqItem.objects.all().delete()
        Article.objects.all().delete()
        Brand.objects.all().delete()
        Service.objects.all().delete()
        restored = restore_backup(backup.name)

        self.assertEqual(restored, 4)
        restored_service = Service.objects.get(slug="inverter-repair")
        restored_brand = Brand.objects.get(slug="example-brand")
        restored_article = Article.objects.get(slug="repair-guide")
        restored_faq = FaqItem.objects.get(question_fa="پرسش؟")
        self.assertEqual(list(restored_brand.services.all()), [restored_service])
        self.assertEqual(list(restored_article.services.all()), [restored_service])
        self.assertEqual(list(restored_article.brands.all()), [restored_brand])
        self.assertEqual(restored_faq.article, restored_article)

    def test_admin_page_can_create_backup(self):
        self.make_content()
        user = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="password",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("content-backups"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "پشتیبان‌گیری محتوا")

        response = self.client.post(reverse("content-backups"), {"action": "export"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(list(Path(self.temp_dir.name).glob("content-*.json"))), 1)
