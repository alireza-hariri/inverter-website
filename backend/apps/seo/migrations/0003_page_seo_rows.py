from django.db import migrations

PAGES = ("home", "services", "brands", "articles", "about", "contact")


def create_pages(apps, schema_editor):
    """Every fixed page gets its row up front, so the SEO editor finds all six to fill in."""
    PageSeo = apps.get_model("seo", "PageSeo")
    for page in PAGES:
        PageSeo.objects.get_or_create(page=page)


def fix_schema_types(apps, schema_editor):
    """Everything defaulted to "Service"; articles and brands are not services."""
    apps.get_model("content", "Article").objects.filter(schema_type__in=("", "Service")).update(schema_type="BlogPosting")
    apps.get_model("content", "Brand").objects.filter(schema_type__in=("", "Service")).update(schema_type="Brand")


class Migration(migrations.Migration):
    dependencies = [
        ("seo", "0002_mediafile_notfoundlog_pageseo_and_more"),
        ("content", "0002_article_focus_keyword_en_article_focus_keyword_fa_and_more"),
    ]

    operations = [
        migrations.RunPython(create_pages, migrations.RunPython.noop),
        migrations.RunPython(fix_schema_types, migrations.RunPython.noop),
    ]
