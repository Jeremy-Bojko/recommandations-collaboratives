# Generated by Django 3.2.3 on 2021-11-30 10:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("projects", "0035_create_switchtender_group"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="switchtender",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="projects_managed",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Aiguilleu·r·se",
            ),
        ),
    ]
