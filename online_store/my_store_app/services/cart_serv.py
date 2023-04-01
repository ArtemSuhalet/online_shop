import json
from decimal import Decimal
from typing import Union

from django.conf import settings
from django.shortcuts import get_object_or_404
from my_store_app.models import *

#=========================сервис корзины для зарегистрированного покупателя=======================
class CartService:
    """
    Сервис корзины
    add_to_cart: метод добавления товара в корзину
    remove_from_cart: убирает товар из корзины
    update_product: изменить количество товара в корзине
    get_goods: получение товаров из корзины
    get_quantity: получение количества товаров в корзине
    get_total_sum: получение общей суммы товаров в корзине
    clear: очистка корзины
    """
    def __init__(self, request):
        if request.user.is_authenticated:
            self.cart, _ = Order.objects.get_or_create(defaults={'customer': request.user},
                                                       customer=request.user,
                                                       in_order=False)

        else:
            self.cart = AnonymCart(request)

    def remove_from_cart(self, product_id: int) -> None:
        """
        убрать товар из корзины
        product_id: id товара
        """
        product = get_object_or_404(Product, id=product_id)
        if isinstance(self.cart, Order):
            cart_product = get_object_or_404(OrderProduct, order=self.cart, product=product)
            product.quantity += cart_product.quantity
            product.save()
            cart_product.delete()
            self.cart.save()
        else:
            self.cart.remove(product)

    def add_to_cart(self, product, quantity: int, price: Decimal = 0, update_quantity=False) -> bool:
        """
        изменить количество товара в корзине
        quantity: новое количество
        """
        if isinstance(self.cart, Order):
            cart_product = OrderProduct.objects.filter(order=self.cart, product=product).first()
            if not cart_product:
                cart_product = OrderProduct(order=self.cart,
                                            product=product,
                                            quantity=0,
                                            final_price=price)

            if update_quantity:
                delta = quantity - cart_product.quantity
                if check_stock(product, delta):
                    cart_product.quantity = quantity
                    cart_product.save()
                    self.cart.save()
                    return True

                return False

            else:
                delta = quantity
                if check_stock(product, delta):
                    cart_product.quantity += quantity
                    cart_product.save()
                    self.cart.save()
                    return True

                return False
        else:
            return self.cart.add(product, quantity, update_quantity=update_quantity)

    def update_product(self, product: Product, quantity: int, product_id: int) -> None:
        """
        изменить количество товара в корзине
        quantity: новое количество
        """
        if self.add_to_cart(product, quantity):
            self.remove_from_cart(product_id)

    def get_goods(self):
        """получить товары из корзины"""
        if isinstance(self.cart, Order):
            return self.cart.order_products.all()
        return self.cart

    def get_quantity(self) -> int:
        """получить количество товаров в корзине"""
        return len(self.cart)

    def get_total_sum(self) -> Decimal:
        """получить общую сумму заказа"""
        if isinstance(self.cart, Order):
            return self.cart.total_sum
        return self.cart.total_sum()

    def merge_carts(self, other):
        """Перенос анонимной корзины в корзину зарегистрированного"""
        for item in other.get_goods():
            self.add_to_cart(item['product'], item['quantity'],)
        other.clear()

    def clear(self) -> None:
        """очистить корзину"""
        return self.cart.clear()

    def save(self) -> None:
        """Сохранить корзину (любую сущность)"""
        return self.save()

    def __len__(self):
        """получить общее количество товаров в корзине"""
        return len(self.cart)



#===================================сервис для анонимного покупателя=========================================

class AnonymCart:
    """
    Класс корзины анонимного пользователя
    """
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product: Product, quantity: int = 1, update_quantity: bool = False):
        """Добавление товара в корзину или обновление его количества"""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if update_quantity:
            delta = quantity - self.cart[product_id]['quantity']
            if check_stock(product, delta):
                self.cart[product_id]['quantity'] = quantity
                self.save()
                return True
            return False
        else:
            delta = quantity
            if check_stock(product, delta):
                self.cart[product_id]['quantity'] += quantity
                self.save()
                return True
            return False

    def save(self):
        """Отметка сессии как измененной"""
        self.session.modified = True

    def remove(self, product: Product):
        """Удаление товара из корзины."""
        product_id = str(product.id)
        if product_id in self.cart:
            product.quantity += self.cart[product_id]['quantity']
            product.save()
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """Проходим по товарам корзины и получаем соответствующие объекты Product"""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = float(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self) -> int:
        """Получение количества товаров в корзине"""
        return len(self.cart.values())

    def total_sum(self):
        """Получение общей стоимости товаров в корзине"""
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        """Очистка корзины"""
        del self.session[settings.CART_SESSION_ID]
        self.save()

def check_stock(product: Product, delta) -> bool:
    """ Проверка наличия на складе """
    if product.quantity >= delta:
        product.quantity -= delta
        product.save()
        return True
    return False


class DecimalEncoder(json.JSONEncoder):
    """ Отбрасывает Decimal у объекта из queryset """

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)