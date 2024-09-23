# Generated by Django 4.2.11 on 2024-09-23 12:33

from django.db import migrations
import wagtail.blocks
import wagtail.contrib.table_block.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0003_alter_showcasepage_content_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="showcasepage",
            name="content",
            field=wagtail.fields.StreamField(
                [
                    (
                        "multicol",
                        wagtail.blocks.StreamBlock(
                            [
                                (
                                    "title",
                                    wagtail.blocks.CharBlock(
                                        label="Titre", required=False
                                    ),
                                ),
                                (
                                    "columns",
                                    wagtail.blocks.StructBlock(
                                        [
                                            (
                                                "text",
                                                wagtail.blocks.RichTextBlock(
                                                    label="Texte avec mise en forme"
                                                ),
                                            )
                                        ],
                                        label="Colonne",
                                    ),
                                ),
                            ],
                            label="Multi Colonnes",
                        ),
                    ),
                    ("richtext", wagtail.blocks.RichTextBlock(label="Texte riche")),
                    ("table", wagtail.contrib.table_block.blocks.TableBlock()),
                ],
                verbose_name="Contenu",
            ),
        ),
        migrations.AlterField(
            model_name="simplepage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    ("richtext", wagtail.blocks.RichTextBlock(label="Texte riche")),
                    ("table", wagtail.contrib.table_block.blocks.TableBlock()),
                ],
                verbose_name="Contenu",
            ),
        ),
    ]
