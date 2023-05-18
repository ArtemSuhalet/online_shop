# Generated by Django 4.1.7 on 2023-03-21 16:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        (
            "my_store_app",
            "0003_orderproduct_alter_order_options_remove_order_count_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="ViewedProduct",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("session", models.CharField(blank=True, max_length=100)),
                ("date", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="viewed_list",
                        to="my_store_app.product",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="viewed",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "viewed product",
                "verbose_name_plural": "viewed products",
            },
        ),
    ]
