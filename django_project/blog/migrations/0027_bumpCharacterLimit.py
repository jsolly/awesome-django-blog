# Generated by Django 4.1.2 on 2023-01-05 04:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0026_change_image_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="metadesc",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="post",
            name="metaimg_alt_txt",
            field=models.CharField(default="John Solly Headshot", max_length=500),
        ),
        migrations.AlterField(
            model_name="post",
            name="metaimg_attribution",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="post",
            name="title",
            field=models.CharField(max_length=250),
        ),
    ]
