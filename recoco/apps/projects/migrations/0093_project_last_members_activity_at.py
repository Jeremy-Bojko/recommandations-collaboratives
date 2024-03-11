# Generated by Django 3.2.18 on 2023-10-10 06:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0092_inactive_flag"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="last_members_activity_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                editable=False,
                verbose_name="Dernière activité de la collectivité",
            ),
        ),
    ]