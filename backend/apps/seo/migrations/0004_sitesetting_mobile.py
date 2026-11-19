from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("seo", "0003_page_seo_rows"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesetting",
            name="mobile",
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
