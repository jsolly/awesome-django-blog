# Generated by Django 3.2.7 on 2022-03-20 13:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0010_add_length_constraints_to_text_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="draft",
            field=models.BooleanField(default=False),
        ),
    ]
