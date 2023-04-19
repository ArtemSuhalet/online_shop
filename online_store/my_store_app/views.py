import datetime
import re
import time
from typing import Dict, Callable, Union, Iterable
from django import template
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views import View, generic
from django.views.generic import DetailView, ListView
from my_store_app.models import *
from my_store_app.forms import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth.models import User
import os
import random
from my_store_app.services.serv_goods import CatalogByCategoriesMixin
from my_store_app.services.good_detail import CurrentProduct, context_pagination
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
#from my_store_app.services.cart_serv import CartService, check_stock, DecimalEncoder, AnonymCart
#import braintree
from my_store_app.services.serv_goods import get_categories

from my_store_app.services.cart import Cart

from my_store_app.models import Order


# ====================регистрация и аутентификация =====================================================================


def register_view(request):  # +
    """Функция регистрации нового пользователя"""

    if request.method == 'POST':
        form = AuthorRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            full_name = form.cleaned_data.get('full_name')
            phone = form.cleaned_data.get('phone')
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password')
            username = form.cleaned_data.get('login')
            user = User.objects.create_user(username=username, first_name=full_name, email=email)
            user.set_password(raw_password)
            user.save()
            login(request, user)
            Profile.objects.create(user=user, username=username, full_name=full_name, phone=phone, email=email)
        return redirect('/')

    return render(request, 'register.html')


class AuthorLogoutView(LogoutView):  # +
    """Выход из учетной записи"""
    next_page = '/'


class Login(LoginView):
    """Вход в учетную запись"""
    def form_valid(self, form):
        return super().form_valid(form)


def account_view(request):

    full_name = Profile.objects.get(user=request.user)

    avatar = Profile.objects.get(user=request.user)

    return render(request, 'account.html', context={
                    'full_name': full_name,
                    'avatar': avatar
                })

class UserEditFormView(View):

    def get(self, request):
        user_form = AccountEditForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        return render(request,
                      'profile.html',
                      {'user_form': user_form,
                       'profile_form': profile_form})

    def post(self, request):
        user_form = AccountEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if profile_form.is_valid() and user_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect(request.META.get('HTTP_REFERER'))
        return render(request,
                        'profile.html',
                        {'user_form': user_form,
                        'profile_form': profile_form})



# ==============================================категории товаров========================================================================


class CategoryView(View):
    """Формирование списка категорий, популярных товаров,
     лимитированных, баннеров и путей до изображений этих категорий"""
    def get(self, request):
        date = Product.objects.all()
        file_name_list = []
        for image in date:
            file = os.path.basename(str(image.image))
            file_name_list.append(file)
        categories = ProductCategory.objects.all()
        banner = zip(date, file_name_list)
        try:
            banners = random.choices(list(banner), k=3)
        except IndexError:
            return None
        popular_product = Product.objects.all().order_by('-rating')[:8]
        limited_edition = Product.objects.all().order_by('limited')[:16]
        #banners = Product.objects.all().order_by('-rating')[:3]
        return render(request, 'index.html', {'categories': categories,
                                              'popular_product': popular_product,
                                              'limited_edition': limited_edition,
                                              'banners': banners})

class FullCatalogView(CatalogByCategoriesMixin, View):
    """
    Класс-контроллер для отображения каталога-списка всех товаров
    ::Страница: Каталог
    """

    def get(self, request):
        """
        метод для гет-запроса контроллера для отображения каталога всех товаров с учётом параметров гет-запроса
        возможные параметры
            search - запрос пользователя из поисковой строки
            tag - выбранный тэг
            sort_type - тип сортировки
            page - страница пагинации
            slug - слаг категории товаров
        :return: рендер страницы каталога товаров определенной категории
        """
        # получаем параметры гет-запроса
        search, tag, sort_type, page, slug = self.get_request_params_for_full_catalog(request)

        # получаем товары в соответсвии с параметрами гет-запроса
        row_items_for_catalog, tags = self.get_full_data(tag, search)
        row_items_for_catalog = self.add_sale_prices_in_goods_if_needed(row_items_for_catalog)

        # сортируем товары
        items_for_catalog, *_ = self.simple_sort(row_items_for_catalog, sort_type)

        # пагинатор
        paginator = Paginator(items_for_catalog, 8)
        pages_list = self.custom_pagination_list(paginator, page)
        page_obj = paginator.get_page(page)

        #кастомные параметры для рэнж-инпута в фильтре каталога
        maxi = self.get_max_price(items_for_catalog)
        mini = self.get_min_price(items_for_catalog)
        midi = round((maxi + mini) / 2, 2)

        # настройка кнопок пагинации
        next_page = str(page_obj.next_page_number() if page_obj.has_next() else page_obj.paginator.num_pages)
        prev_page = str(page_obj.previous_page_number() if page_obj.has_previous() else 1)

        return render(
            request,
            'catalog.html',
            context={
                'page_obj': page_obj,
                'sort_type': sort_type,
                'mini': mini,
                'maxi': maxi,
                'midi': midi,
                'next_page': next_page,
                'prev_page': prev_page,
                'pages_list': pages_list,
                'tags': tags,
                'search': search,
                'tag': tag,
            })


class ProductDetailView(DetailView):
    """
    Детальная страница продукта
    ::Страница: Детальная страница продукта
    """
    model = Product
    context_object_name = 'product'
    template_name = 'product.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        product = CurrentProduct(instance=context['product'])
        reviews = product.get_reviews
        cart_product_form = CartAddProductForm()

        context = {
            'reviews_count': reviews.count(),
            'comments': context_pagination(self.request, reviews,
                                           size_page=3),

            'form': ReviewForm(),
            'specifications': product.get_specifications,
            'tags': product.get_tags,
            'cart_product_form': cart_product_form,
            **context
        }
        return context


def get_reviews(request: HttpRequest) -> JsonResponse:
    """
    Представление для получения всех отзывов о товаре
    ::Страница: Детальная страница продукта
    """
    slug = request.GET.get('slug')
    page = request.GET.get('page')
    product = CurrentProduct(slug=slug)
    reviews = product.get_reviews
    return JsonResponse({**product.get_review_page(reviews, page),
                         'slug': slug}, safe=False)


def post_review(request: HttpRequest):
    """
    Представление для добавления отзыва о продукте
    ::Страница: Детальная страница продукта
    """
    slug = request.POST.get('slug')
    product = CurrentProduct(slug=slug)
    form = ReviewForm(request.POST)
    if form.is_valid():

        ProductComment.objects.create(**form.cleaned_data)
        product.update_product_rating()

    return redirect(request.META.get('HTTP_REFERER'))




register = template.Library()


@register.simple_tag()
def get_tree_dict() -> Dict:
    categories = get_categories()
    res_dict = dict()
    for elem in categories:
        if elem.id:
            res_dict.setdefault(elem.name, [])
            res_dict[elem.name].append(elem)
        else:
            res_dict.setdefault(elem, [])
    return res_dict



#===================================заказы/корзина/оплата=============================================



def add_viewed(request, product_id):
    """
    Добавление в список просмотренных товаров
    ::Страница: Детальная страница товара
    """

    product = Product.objects.get(id=product_id)
    if request.user.is_anonymous:
        ViewedProduct.objects.get_or_create(session=request.session.session_key,
                                            product=product)
    else:
        ViewedProduct.objects.get_or_create(user=request.user,
                                            product=product)
    return redirect(reverse('product', kwargs={'slug': product.slug}))


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 update_quantity=cd['update'])
    return redirect('cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={'quantity':item['quantity'],
                                                                   'update':True
                                                                   })

    return render(request, 'cart.html', {'cart': cart})

#==========================================оформление заказа=============================




def orderstepone(request, **kwargs ):
    """
    Представление первого шага оформления заказа
    ::Страница: Оформление заказа
    """

    if request.method == 'POST':
        form = OrderStepOneForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                order = form.save()

                cart = Cart(request)
                for item in cart:
                    OrderProduct.objects.create(order=order,
                                                    product=item['product'],
                                                    final_price=item['price'],
                                                    quantity=item['quantity'])
                order.save()
                kwargs = {}
                kwargs['order_id'] = order.id
                order_id = order.id
                return redirect('order_step_two', order_id)
            else:
                return redirect('login')
        return render(request, 'order_step_two.html', {'form': form})
    else:
        user = request.user
        if user.is_authenticated:
            initial = {'fio': f'{user.profile.full_name}',
                            'email': user.profile.email,
                            'phone': user.profile.phone,
                            'delivery': 'exp',
                            'payment': 'cash'}
        else:
            initial = {'delivery': 'exp',
                        'payment': 'cash'
                       }
        form = OrderStepOneForm(initial=initial)

        return render(request, 'order_step_one.html', {'form': form})


def ordersteptwo(request, order_id, delivery_cost=None, **kwargs):
    """
    Представление второго шага оформления заказа
    ::Страница: Оформление заказа
    """

    if request.method == 'POST':
        form = OrderStepTwoForm(request.POST)
        order = Order.objects.get(id=order_id)
        if form.is_valid():
            delivery = form.cleaned_data['delivery']
            city = form.cleaned_data['city']
            address = form.cleaned_data['address']

            order.delivery = delivery
            order.city = city
            order.address = address
            order.customer = request.user
            if order.delivery == 'reg':
                if order.total_sum > 20:
                    order.delivery_cost = int(2)
                else:
                    order.delivery_cost = int(0)
            elif order.delivery == 'exp':
                order.delivery_cost = int(5)
            order.save()
            kwargs = {}
            kwargs['order_id'] = order.id
            return redirect('order_step_three', order_id)
        return render(request, 'order_step_two.html', {'form': form, 'order_id':order_id})
    else:
        order = Order.objects.get(id=order_id)
        user = request.user
        if user.is_authenticated:
            initial = {
                       'delivery': 'reg',
                       'payment': 'cash'}

            form = OrderStepTwoForm(initial=initial)
            kwargs = {}
            kwargs['order_id'] = order.id
            return render(request, 'order_step_two.html', {'form': form, 'order_id':order_id})
        else:
            return redirect('login')



class OrderStepOneAnonym(View):
    """
    Представление первого шага оформления заказа для анонимного пользователя
    ::Страница: Оформление заказа
    """
    def get(self, request: HttpRequest) -> Callable:
        if request.user.is_authenticated:
            return redirect('order_step_one')

        form = RegisterForm()

        context = {'form': form}
        return render(request, 'order_step_one_anonimous.html', context=context)

    def post(self, request: HttpRequest) -> Callable:
        """
        Метод переопределен для слияние анонимной корзины
        с корзиной аутентифицированного пользователя
        """
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            old_cart = Cart(self.request)
            user = form.save()
            reset_phone_format(instance=user)
            login(request, get_auth_user(data=form.cleaned_data))
            new_cart = Cart(self.request)
            new_cart = old_cart


            order = Order.objects.get(customer=request.user, in_order=False)
            fio = request.POST.get('name')
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']

            if fio:
                order.fio = fio
            order.email = email
            order.phone = phone
            order.save()
            return redirect('order_step_two')

        return render(request, 'order_step_one_anonimous.html', {'form': form})


class OrderStepThree(View):
    """
    Представление третьего шага оформления заказа
    ::Страница: Оформление заказа
    """
    form_class = OrderStepThreeForm
    template_name = 'order_step_three.html'

    def get(self, request: HttpRequest, order_id):
        user = request.user
        if user.is_authenticated:
            form = OrderStepThreeForm
            return render(request, self.template_name, {'form': form, 'order_id':order_id})
        else:
            return redirect('login')

    def post(self, request: HttpRequest, order_id):
        form = self.form_class(request.POST)
        order = Order.objects.get(id=order_id)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            order.payment_method = payment_method
            order.in_order = True
            order.ordered = datetime.datetime.today()
            order.save()
            return redirect('order_step_four', order_id)

        return render(request, self.template_name, {'form': form, 'order_id':order_id})


class OrderStepFour(View):
    """
    Представление четвертого шага оформления заказа
    ::Страница: Оформление заказа
    """
    template_name = 'order_step_four.html'

    def get(self, request: HttpRequest, order_id):
        user = request.user
        if user.is_authenticated:
            order = Order.objects.filter(id=order_id, in_order=True).last()
            return render(request, self.template_name, {'order': order, 'order_id':order_id})

        else:
            return redirect('login')

def get_auth_user(data: Dict) -> Callable:
    """
    Authentication user
    """
    email = data['email']
    raw_password = data['password1']
    return authenticate(email=email, password=raw_password)


def reset_phone_format(instance: 'User') -> None:
    """
    Reset phone format
    """
    try:
        instance.phone = instance.phone[3:].replace(')', '').replace('-', '')
        instance.save(update_fields=['phone'])
    except AttributeError:
        pass


class PaymentView(View):
    """
    Оплата заказа. Логика направляется в зависимости от способа оплаты.
    ::Страница: Оплата заказа
    """
    def get(self, request: HttpRequest, order_id):
        order = get_object_or_404(Order, id=order_id)
        if order.payment_method == 'card':
            return redirect('payment_with_card', order_id)
        else:
            return redirect('payment_with_account', order_id)


class PaymentWithCardView(View):
    """
    Представление оплаты банковской картой
    ::Страница: Оплата заказа
    """
    template_name = 'paymentcard.html'

    def get(self, request: HttpRequest, order_id: int):
        form = PaymentForm(request.POST)
        try:
            order = get_object_or_404(Order, id=order_id)
        except Http404:
            order = None
        context = {'order': order, 'order_id': order_id, 'form': form}
        return render(request, self.template_name, context=context)

    def post(self, request: HttpRequest, order_id):
        order = get_object_or_404(Order, id=order_id)

        form = PaymentForm(request.POST)

        if form.is_valid():

            user = request.user

            number = form.cleaned_data.get('number')
            name = form.cleaned_data.get('name')
            code = form.cleaned_data.get('code')

            Payment.objects.create(
                number=number,
                name=user.profile.username,
                code=order_id,

            )

            return redirect('payment_process', order_id)
        return render(request, self.template_name, context={'form': form, 'order_id': order_id})


class PaymentWithAccountView(View):
    """
    Представление оплаты рандомным счетом
    ::Страница: Оплата заказа
    """
    template_name = 'paymentaccount.html'

    # def get(self, request: HttpRequest, order_id: int):
    #     order = get_object_or_404(Order, id=order_id)
    #     context = {'order': order, 'order_id': order_id}
    #     return render(request, self.template_name, context=context)
    #
    # def post(self, request: HttpRequest, order_id: int):
    #     account = ''.join(request.POST.get('numero1').split(' '))
    #     print(account, 'ygeyuwghdjsbvb')
    #     form = PaymentForm(request.POST)
    #
    #     if form.is_valid():
    #         user = request.user
    #
    #         number = form.cleaned_data.get('number')
    #         name = form.cleaned_data.get('name')
    #         code = form.cleaned_data.get('code')
    #
    #         Payment.objects.create(
    #             number=account,
    #             name=user.profile.username,
    #             code=order_id,
    #
    #         )
    #         return redirect('payment_process', order_id)
    #     return render(request, self.template_name, context={'form': form, 'order_id': order_id})
    #     #result = process_payment(order_id, account)

    def get(self, request: HttpRequest, order_id: int):
        order = get_object_or_404(Order, id=order_id)
        card = randomnumber()
        print('number', card)
        initial = {'number': card
                   }
        form = PaymentForm(initial=initial)

        context = {'order': order, 'order_id': order_id, 'form': form}
        return render(request, self.template_name, context=context)

    def post(self, request: HttpRequest, order_id):
        order = get_object_or_404(Order, id=order_id)
        # card = randomnumber()
        # print('number', card)
        form = PaymentForm(request.POST)

        if form.is_valid():

            user = request.user

            number = form.cleaned_data.get('number')
            name = form.cleaned_data.get('name')
            code = form.cleaned_data.get('code')


            Payment.objects.create(
                number=number,
                name=user.profile.username,
                code=order_id,

            )

            return redirect('payment_process', order_id)
        return render(request, self.template_name, context={'form': form, 'order_id': order_id})

def randomnumber():

    characters = list('1234567890')
    number = ''
    for x in range(8):
        number += random.choice(characters)
    print(number, 'random')
    return number

def payment_process(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    pay = get_object_or_404(Payment, code=order_id)
    print(type(pay.number), 'fqlb')
    if pay.number % 10 == 0 or len(str(pay.number)) % 2 != 0:
        order.payment_error = random.choice('IndexError', 'KeyError', 'ValueError', 'Http404')
        order.save()
        time.sleep(3)
        return redirect('payment_canceled')
    order.paid = True
    order.save()
    time.sleep(3)
    return redirect('payment_done')

def payment_done(request):
    """
    Представление удачной оплаты
    ::Страница: Оплата заказа
    """
    return render(request, 'done.html')


def payment_canceled(request):
    """
    Представление неудачной оплаты
    ::Страница: Оплата заказа
    """
    return render(request, 'canceled.html')

class HistoryOrderView(generic.ListView):
    """
    Представление истории заказов
    ::Страница: История заказов
    """

    model = Order
    context_object_name = 'orders'
    template_name = 'order_list.html'

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user, in_order=True)



class HistoryOrderDetail(DetailView):
    """
    Детальное представление заказа
    ::Страница: Детальная страница заказа
    """

    model = Order

    def get(self, request, *args, **kwargs):
        """ Получить заказ """

        pk = kwargs['order_id']
        order = self.model.objects.prefetch_related('order_products').get(id=pk)
        return render(request, 'history_detail.html', context={'order': order})
