# Generated by Django 4.1.7 on 2023-05-05 14:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("my_store_app", "0008_product_free_delivery"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="free_delivery",
            new_name="is_free_delivery",
        ),
    ]
