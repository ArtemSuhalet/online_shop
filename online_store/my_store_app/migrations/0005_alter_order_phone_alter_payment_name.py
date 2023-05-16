# Generated by Django 4.1.7 on 2023-04-16 15:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_store_app', '0004_viewedproduct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='phone',
            field=models.CharField(blank=True, max_length=16, null=True, validators=[django.core.validators.RegexValidator(message='номер телефона необходимо вводить в формате: +999999999 до 15 символов.', regex='^\\+?1?\\d{6,15}$')], verbose_name='phone number'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='name',
            field=models.TextField(default='не указан', max_length=30, null=True),
        ),
    ]