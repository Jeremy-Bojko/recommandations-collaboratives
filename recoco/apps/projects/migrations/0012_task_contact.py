# Generated by Django 3.2.3 on 2021-07-20 07:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("addressbook", "0002_auto_20210720_0948"),
        ("projects", "0011_project_commune"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="contact",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="addressbook.contact",
            ),
        ),
    ]
