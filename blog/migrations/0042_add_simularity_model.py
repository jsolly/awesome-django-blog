# Generated by Django 4.2.5 on 2023-11-08 23:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0041_disallow_null_values_date_updated"),
    ]

    operations = [
        migrations.CreateModel(
            name="Similarity",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("score", models.FloatField()),
                (
                    "post1",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="similarities1",
                        to="blog.post",
                    ),
                ),
                (
                    "post2",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="similarities2",
                        to="blog.post",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="similarity",
            constraint=models.UniqueConstraint(
                fields=("post1", "post2"), name="unique_pair"
            ),
        ),
    ]