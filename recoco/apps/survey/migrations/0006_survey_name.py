# Generated by Django 3.2.3 on 2021-08-03 08:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("survey", "0005_auto_20210727_1716"),
    ]

    operations = [
        migrations.AddField(
            model_name="survey",
            name="name",
            field=models.CharField(default="Sans Nom", max_length=80),
            preserve_default=False,
        ),
    ]
