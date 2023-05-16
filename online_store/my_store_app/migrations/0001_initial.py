# Generated by Django 4.1.7 on 2023-03-12 15:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import my_store_app.models
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0005_auto_20220424_2025'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(default=0, verbose_name='номер счета')),
                ('name', models.TextField(default='не указан', max_length=30)),
                ('month', models.DateField(auto_now_add=True)),
                ('year', models.DateField(auto_now_add=True)),
                ('code', models.IntegerField(default=0, verbose_name='код оплаты')),
            ],
            options={
                'verbose_name': 'Оплата',
                'verbose_name_plural': 'Оплата',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='product name')),
                ('code', models.CharField(blank=True, max_length=10, null=True, verbose_name='product code')),
                ('slug', models.SlugField(unique=True, verbose_name='product slug')),
                ('image', models.ImageField(upload_to='', verbose_name='product image')),
                ('description', models.TextField(max_length=2550, null=True, verbose_name='product description')),
                ('rating', models.FloatField(default=0, null=True, verbose_name='rating')),
                ('is_published', models.BooleanField(blank=True, default=True, null=True, verbose_name='is published')),
                ('limited', models.BooleanField(default=False, verbose_name='limited edition')),
            ],
            options={
                'verbose_name': 'product',
                'verbose_name_plural': 'products',
                'db_table': 'products',
            },
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, null=True, verbose_name='category title')),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
                ('description', models.TextField(blank=True, max_length=255, null=True, verbose_name='description')),
                ('icon', models.ImageField(upload_to='', verbose_name='icon')),
                ('image', models.ImageField(upload_to='', verbose_name='image')),
            ],
            options={
                'verbose_name': 'product category',
                'verbose_name_plural': 'product categories',
            },
        ),
        migrations.CreateModel(
            name='Specifications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=32)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='specifications', to='my_store_app.product')),
            ],
            options={
                'verbose_name': 'specification',
                'verbose_name_plural': 'specifications',
                'db_table': 'specifications',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, default='-------', max_length=50, null=True, verbose_name='username')),
                ('full_name', models.CharField(blank=True, default='не указано', max_length=50, verbose_name='ФИО пользователя')),
                ('phone', models.CharField(blank=True, default='Не указано', max_length=30, null=True, unique=True, verbose_name='номер телефона')),
                ('email', models.EmailField(blank=True, max_length=254, unique=True, verbose_name='email пользователя')),
                ('avatar', models.ImageField(default='', null=True, upload_to='catalog/files/', validators=[my_store_app.models.Profile.validate_image])),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Профиль',
                'verbose_name_plural': 'Профили пользователей',
            },
        ),
        migrations.CreateModel(
            name='ProductComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(max_length=25, null=True, verbose_name='author')),
                ('content', models.TextField(max_length=255, null=True, verbose_name='content')),
                ('added', models.DateTimeField(auto_now_add=True, null=True, verbose_name='added')),
                ('rating', models.IntegerField(verbose_name='rating')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_comments', to='my_store_app.product')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'product comment',
                'verbose_name_plural': 'product comments',
                'db_table': 'comments',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='my_store_app.productcategory', verbose_name='good_category'),
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.CreateModel(
            name='OrderHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_date', models.DateField(auto_now_add=True)),
                ('delivery_type', models.TextField(default='не указан', max_length=30, verbose_name='способ доставки')),
                ('payment_type', models.TextField(default='не указан', max_length=30, verbose_name='способ оплаты')),
                ('total_cost', models.IntegerField(default=0, verbose_name='общая стоимость заказа')),
                ('status', models.TextField(default='не указан', max_length=30, verbose_name='статус оплаты')),
                ('city', models.TextField(default='не указан', max_length=30, verbose_name='город доставки')),
                ('address', models.TextField(default='не указан', max_length=30, verbose_name='адрес доставки')),
                ('product_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_store_app.product', verbose_name='товар')),
                ('user_order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='my_store_app.profile', verbose_name='пользователь')),
            ],
            options={
                'verbose_name': 'История покупок',
                'verbose_name_plural': 'Истории покупок',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(default=0, verbose_name='колличество  товаров в корзине')),
                ('price', models.IntegerField(default=0, verbose_name='общая стоимость  товаров в корзине')),
                ('date', models.DateField(auto_now_add=True)),
                ('free_delivery', models.BooleanField(default=False, verbose_name='наличие бесплатной доставки')),
                ('product_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_store_app.product', verbose_name='товар')),
            ],
            options={
                'verbose_name': 'Покупка',
                'verbose_name_plural': 'Покупки',
            },
        ),
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_at', models.DateField(auto_now_add=True)),
                ('product', models.ManyToManyField(related_name='product', to='my_store_app.product')),
                ('username', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='my_store_app.profile')),
            ],
            options={
                'verbose_name': 'Корзина',
                'verbose_name_plural': 'Корзины',
            },
        ),
    ]
