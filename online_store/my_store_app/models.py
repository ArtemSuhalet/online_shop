from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError


class Profile(models.Model):
    def validate_image(fieldfile_obj):
        file_size = fieldfile_obj.file.size
        megabyte_limit = 150.0
        if file_size > megabyte_limit * 1024 * 1024:
            raise ValidationError("Максимальный размер файла {}MB".format(str(megabyte_limit)))

    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(default='-------', max_length=50,
                                verbose_name='username', blank=True, null=True)
    full_name = models.CharField(default='не указано', max_length=50, verbose_name='ФИО пользователя', blank=True)
    phone = models.CharField(default='Не указано', max_length=30, verbose_name='номер телефона', blank=True, null=True,
                             unique=True)
    email = models.EmailField(verbose_name='email пользователя', blank=True, unique=True)
    avatar = models.ImageField(upload_to='catalog/files/', null=True, validators=[validate_image], default='')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return self.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        Profile.objects.create(user=instance)


class Sales(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='товар')
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, verbose_name='магазин')
    count = models.IntegerField(default=0, verbose_name='количество товара по скидке')
    dateFrom = models.DateField()
    dateTo = models.DateField()

    class Meta:
        verbose_name = 'Распродажа'
        verbose_name_plural = 'Распродажа'


class CategoryProduct(models.Model):  # категория товаров
    title = models.TextField(max_length=50, verbose_name='название категории')
    image = models.FileField(upload_to='my_store_app/static/', null=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Product(models.Model):  # товар
    category = models.ForeignKey('CategoryProduct', on_delete=models.CASCADE, verbose_name='категория товара')
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, verbose_name='магазин товара')
    specifications = models.ForeignKey('Specifications', on_delete=models.CASCADE, verbose_name='спецификация товара')
    price = models.IntegerField(default=0, verbose_name='цена товара')
    count = models.IntegerField(default=0, verbose_name='количество ')
    date = models.DateField(auto_now_add=True)
    title = models.TextField(max_length=50, verbose_name='название товара')
    description = models.TextField(max_length=100, verbose_name='описание товара')
    free_delivery = models.BooleanField(default=True)
    product_picture = models.ImageField(upload_to='my_store_app/static/', null=True)
    rating = models.IntegerField(default=0, verbose_name='счетчик покупок данного товара')
    reviews = models.IntegerField(default=0, verbose_name='счетчик просмотров данного товара')
    tags = models.ManyToManyField('TagsFile', related_name='tags')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.title


class TagsFile(models.Model):
    tags_name = models.TextField(max_length=50, verbose_name='тэг товара')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.tags_name


class Shop(models.Model):
    shop_name = models.TextField(max_length=50, verbose_name='название магазина')

    class Meta:
        verbose_name = 'магазин'
        verbose_name_plural = 'магазины'

    def __str__(self):
        return self.shop_name


class Reviews(models.Model):  # отзыв
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='товар',
                                related_name='product_title_product_set')
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='пользователь')
    text = models.CharField(default='Не указано', max_length=100, verbose_name='текст отзыва', blank=True)
    create_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text


class Specifications(models.Model):
    name = models.TextField(max_length=50, verbose_name='название')
    value = models.TextField(max_length=50, verbose_name='значение')

    class Meta:
        verbose_name = 'Спецификация'
        verbose_name_plural = 'Спецификации'

    def __str__(self):
        return self.name


class OrderHistory(models.Model):  # история покупок пользователя
    user_order = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='пользователь', null=True)
    product_order = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='товар')
    payment_date = models.DateField(auto_now_add=True)
    delivery_type = models.TextField(max_length=30, default='не указан', verbose_name='способ доставки')
    payment_type = models.TextField(max_length=30, default='не указан', verbose_name='способ оплаты')
    total_cost = models.IntegerField(default=0, verbose_name='общая стоимость заказа')
    status = models.TextField(max_length=30, default='не указан', verbose_name='статус оплаты')
    city = models.TextField(max_length=30, default='не указан', verbose_name='город доставки')
    address = models.TextField(max_length=30, default='не указан', verbose_name='адрес доставки')

    class Meta:
        verbose_name = 'История покупок'
        verbose_name_plural = 'Истории покупок'

    def __str__(self):
        return self.user_order.name


class Order(models.Model):  # покупка товаров из корзины
    product_order = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name='товар')
    count = models.IntegerField(default=0, verbose_name='колличество  товаров в корзине')
    price = models.IntegerField(default=0, verbose_name='общая стоимость  товаров в корзине')
    date = models.DateField(auto_now_add=True)
    free_delivery = models.BooleanField(default=False, verbose_name='наличие бесплатной доставки')

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'

    def __str__(self):
        return self.product_order


class Basket(models.Model):  # корзина пользователя
    username = models.OneToOneField(Profile, unique=True, on_delete=models.CASCADE, related_name='profile')
    product = models.ManyToManyField('Product', related_name='product')
    create_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Payment(models.Model):
    number = models.IntegerField(default=0, verbose_name='номер счета')
    name = models.TextField(max_length=30, default='не указан')
    month = models.DateField(auto_now_add=True)
    year = models.DateField(auto_now_add=True)
    code = models.IntegerField(default=0, verbose_name='код оплаты')

    class Meta:
        verbose_name = 'Оплата'
        verbose_name_plural = 'Оплата'

    def __str__(self):
        return self.name