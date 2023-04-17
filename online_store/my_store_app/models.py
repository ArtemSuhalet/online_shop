from _decimal import Decimal
from typing import Callable
from django.core.validators import RegexValidator
from django.db.models import QuerySet
from django.urls import reverse
from taggit.managers import TaggableManager
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


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

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        Profile.objects.create(user=instance)


class ProductCategory(models.Model):
    """
    Модель категории товаров
    """
    name = models.CharField(
        max_length=25,
        null=True,
        verbose_name=_('category title')
    )
    slug = models.SlugField(verbose_name=_('slug'), unique=True)
    description = models.TextField(max_length=255, null=True, blank=True, verbose_name=_('description'))
    icon = models.ImageField(verbose_name=_('icon'))
    image = models.ImageField(verbose_name=_('image'))

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = _('product categories')
        verbose_name = _('product category')


    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

    @property
    def icon_url(self):
        if self.icon and hasattr(self.icon, 'url'):
            return self.icon.url



class Product(models.Model):
    """
    Модель товара
    """
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='good_category',
    )
    name = models.CharField(max_length=100, verbose_name=_('product name'))
    code = models.CharField(max_length=10, null=True, blank=True, verbose_name=_('product code'))
    slug = models.SlugField(db_index=True, verbose_name=_('product slug'), unique=True)
    image = models.ImageField(verbose_name=_('product image'))
    description = models.TextField(max_length=2550, null=True, verbose_name=_('product description'))
    rating = models.FloatField(null=True, default=0, verbose_name=_('rating'))
    is_published = models.BooleanField(verbose_name=_('is published'), null=True, blank=True, default=True)
    tags = TaggableManager()
    limited = models.BooleanField(default=False, verbose_name=_('limited edition'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('price'))
    quantity = models.IntegerField(verbose_name=_('quantity'))

    def __str__(self):
        return self.name

    def get_absolute_url(self) -> Callable:
        return reverse('product', kwargs={'slug': self.slug})

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        db_table = 'products'


class ProductComment(models.Model):
    """
    Модель комментария к товару
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_comments')
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    author = models.CharField(verbose_name=_('author'), max_length=25, null=True)
    content = models.TextField(verbose_name=_('content'), max_length=255, null=True)
    added = models.DateTimeField(verbose_name=_('added'), auto_now_add=True, null=True)
    rating = models.IntegerField(verbose_name=_('rating'))

    def __str__(self) -> str:
        return f'Comments for {str(self.product)}'

    class Meta:
        verbose_name = _('product comment')
        verbose_name_plural = _('product comments')
        db_table = 'comments'


class Specifications(models.Model):
    """ Модель Характеристики товара """

    value = models.CharField(max_length=32, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True, related_name='specifications')

    def __str__(self) -> str:
        return self.value

    class Meta:
        verbose_name = _('specification')
        verbose_name_plural = _('specifications')
        db_table = 'specifications'

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


#====================================модели заказа==========================================================

class Order(models.Model):
    """
    Модель заказа
    """
    DELIVERY_CHOICES = [
        ('reg', _('Regular')),
        ('exp', _('Express'))
    ]

    PAYMENT_CHOICES = [
        ('card', _('Bank Card')),
        ('cash', _('From random account')),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE,
                                 null=True,
                                 related_name='orders',
                                 verbose_name=_('customer'))
    fio = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('name and lastname'))

    phone_valid = RegexValidator(regex=r'^\+?1?\d{6,15}$',
                                 message=' '.join([str(_('номер телефона необходимо вводить в формате:')), '+999999999',
                                                   str(_('до 15 символов.'))]))
    phone = models.CharField(max_length=16, validators=[phone_valid],
                             null=True, blank=True, verbose_name=_('phone number'))

    email = models.EmailField(null=True, blank=True, verbose_name=_('email'))

    delivery = models.CharField(max_length=3,
                                choices=DELIVERY_CHOICES, default='reg', verbose_name=_('delivery'))

    payment_method = models.CharField(max_length=4,
                                      choices=PAYMENT_CHOICES,
                                      default='card',
                                      verbose_name=_('payment method'))

    city = models.CharField(max_length=25, null=True, blank=True, verbose_name=_('city'))
    address = models.TextField(max_length=255, null=True, blank=True, verbose_name=_('address'))

    in_order = models.BooleanField(default=False, verbose_name=_('in order'))
    paid = models.BooleanField(default=False, verbose_name=_('order is payed'))
    payment_error = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('payment error'))

    ordered = models.DateTimeField(null=True, blank=True, verbose_name=_('order placement date'))
    braintree_id = models.CharField(max_length=150, blank=True, verbose_name=_('transaction id'))

    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Delivery cost'))

    @property
    def total_sum(self) -> Decimal:
        """Метод получения общей стоимости товаров в заказе"""
        total = Decimal(0.00)
        for product in self.order_products.all():
            total += product.final_price * product.quantity + product.order.delivery_cost
        return Decimal(total)


    def __str__(self):
        return f'{_("Order")} №{self.id}'

    def name(self):
        return self.__str__()

    def __len__(self) -> int:
        """Метод получения количества товаров в заказе"""
        return len(self.order_products.all())

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')


class OrderProduct(models.Model):
    """
    Модель товара в заказе
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_products'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_products'
    )
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                      verbose_name=_('final_price'))
    quantity = models.IntegerField(null=True, default=1,
                                   verbose_name=_('quantity'))

    def __str__(self):
        return f"{_('OrderProduct')} №{self.id}"

    def name(self):
        return self.__str__()

    class Meta:
        verbose_name = _('order product')
        verbose_name_plural = _('order products')



class ViewedProduct(models.Model):
    """ Модель просмотренного товара """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed', blank=True, null=True)
    session = models.CharField(max_length=100, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='viewed_list')
    date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('viewed product')
        verbose_name_plural = _('viewed products')

class Payment(models.Model):
    number_valid = RegexValidator(regex=r'^\+?1?\d{6,8}$',
                                 message=' '.join([str(_('номер  необходимо вводить в формате:')), '999999999',
                                                   str(_('до 8 символов.'))]))
    number = models.IntegerField(default=0, validators=[number_valid], verbose_name='номер счета')
    name = models.TextField(null=True, max_length=30, default='не указан')
    month = models.DateField(auto_now_add=True)
    year = models.DateField(auto_now_add=True)
    code = models.IntegerField(default=0, verbose_name='код оплаты')


    class Meta:
        verbose_name = 'Оплата'
        verbose_name_plural = 'Оплата'

    def __str__(self):
        return "%s"%self.name


