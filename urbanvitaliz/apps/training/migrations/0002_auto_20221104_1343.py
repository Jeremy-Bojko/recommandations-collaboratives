# Generated by Django 3.2.16 on 2022-11-04 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0001_initial_squashed_0006_auto_20221104_1324'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='challenge',
            managers=[
            ],
        ),
        migrations.AlterField(
            model_name='challengedefinition',
            name='code',
            field=models.SlugField(max_length=128, unique=True),
        ),
    ]