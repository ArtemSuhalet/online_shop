# Generated by Django 4.1.7 on 2023-04-27 13:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("admin_app", "0002_alter_file_file"),
    ]

    operations = [
        migrations.AlterField(
            model_name="file",
            name="file",
            field=models.FileField(upload_to="static/"),
        ),
    ]
