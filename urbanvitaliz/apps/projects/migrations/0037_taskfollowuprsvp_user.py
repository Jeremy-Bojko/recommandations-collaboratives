# Generated by Django 3.2.3 on 2021-12-06 17:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("projects", "0036_project_switchtender"),
    ]

    operations = [
        migrations.AddField(
            model_name="taskfollowuprsvp",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="rsvp_followups",
                to="auth.user",
            ),
            preserve_default=False,
        ),
    ]
