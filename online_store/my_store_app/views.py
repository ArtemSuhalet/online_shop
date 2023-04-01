from typing import Dict, Callable, Union, Iterable
from django import template
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import DetailView
from my_store_app.models import *
from my_store_app.forms import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth.models import User
import os
from my_store_app.services.serv_goods import CatalogByCategoriesMixin
from my_store_app.services.good_detail import CurrentProduct, context_pagination
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
#from my_store_app.services.cart_serv import CartService, check_stock, DecimalEncoder, AnonymCart

from my_store_app.services.serv_goods import get_categories

from my_store_app.services.cart import Cart


# ====================регистрация и аутентификация =====================================================================


def register_view(request):  # +
    """Функция регистрации нового пользователя"""

    if request.method == 'POST':
        form = AuthorRegisterForm(request.POST)
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

        profile_form = ProfileForm(instance=request.user.profile)
        return render(request, 'profile.html', context={'profile_form': profile_form})

    def post(self, request):

        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if profile_form.is_valid():
            profile_form.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Профиль успешно сохранен!')
            return render(request, 'profile.html', context={'profile_form': profile_form})
        return render(request, 'profile.html', context={'profile_form': profile_form})


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

        category = zip(date, file_name_list)
        popular_product = Product.objects.all().order_by('-rating')[:8]
        limited_edition = Product.objects.all().order_by('limited')
        banners = Product.objects.all().order_by('-rating')
        return render(request, 'index.html', {'categories': category,
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

 #class AllCardForAjax(CatalogByCategoriesMixin, View):

#     """
#     Класс-контроллер для отображения набора товаров в каталоге с учетом необходимых фильтров, сортировки и пагинации
#     ::Страница: Каталог
#     """
#
#     def get(self, request):
#         """
#         метод для гет-запроса контроллера для отображения  набора товаров в каталоге
#         с учетом необходимых фильтров, сортировки и пагинации без обновления изначальной страницы каталога
#         get параметры :
#             search - запрос пользователя из поисковой строки
#             tag - выбранный тэг
#             sort_type - тип сортировки
#             page - страница пагинации
#             slug - слаг категории товаров
#         :param request: искомый запрос клиента
#         :return: json с ключами:
#                 html - текст разметки необходимых карточек товаров с учетов входных условий
#                 current_state - вид и направление текущей использованной сортировки
#                 next_state - тип и направление сортировки для повторного запроса
#                 next_page - значение следующей доступной страницы пагинации
#                 prev_page - значение предыдущей доступной страницы пагинации
#                 pages_list - список доступных номеров страниц пагинации при данных входных условиях
#         """
#
#         search, tag, sort_type, page, slug = self.get_request_params_for_full_catalog(request)
#
#         if not self.check_if_filter_params(request):
#             # получаем товары без фильтра и актуальные стоимости
#             row_items_for_catalog, tags = self.get_full_data(tag, search, slug)
#             row_items_for_catalog = self.add_sale_prices_in_goods_if_needed(row_items_for_catalog)
#
#         else:
#             # получаем товары с фильтром и актуальные стоимости
#             filter_data = self.get_data_from_form(request)
#             row_items_for_catalog, tags = self.get_full_data_with_filters(
#                 search_query=search,
#                 search_tag=tag,
#                 slug=slug,
#                 filter_data=filter_data
#             )
#
#         items_for_catalog, next_state = self.simple_sort(row_items_for_catalog, sort_type)
#
#         # пагинатор
#         paginator = Paginator(items_for_catalog, 8)
#
#         pages_list = self.custom_pagination_list(paginator, page)
#         page_obj = paginator.get_page(page)
#
#         # кнопки пагинации
#         next_page = str(page_obj.next_page_number() if page_obj.has_next() else page_obj.paginator.num_pages)
#         prev_page = str(page_obj.previous_page_number() if page_obj.has_previous() else 1)
#
#         context = {
#             'pages_list': pages_list,
#             'page_obj': page_obj,
#             'sort_type': sort_type,
#             'next_page': next_page,
#             'prev_page': prev_page,
#         }
#
#         return JsonResponse({
#             'html': render_to_string('includes/card.html', context=context),
#             'current_state': sort_type,
#             'next_state': next_state,
#             'next_page': next_page,
#             'prev_page': prev_page,
#             'pages_list': pages_list,
#             'sort_type': sort_type,
#         })
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


# def cart_clear(request):
#     """
#     Очистка корзины
#     ::Страница: Корзина
#     """
#     cart = CartService(request)
#     cart.clear()
#     return redirect('cart_detail')
#
# class CartView(View):
#     """
#     Представление корзины
#     ::Страница: Корзина
#     """
#
#     @classmethod
#     def get(cls, request: HttpRequest):
#         cart = CartService(request)
#
#         items = cart.get_goods()
#         total = cart.get_quantity#колво товара в корзине
#         total_price = cart.get_total_sum
#
#         context = {'items': items,
#                    'total': total,
#                    'total_price': total_price
#                    }
#
#         return render(request, 'cart.html', context=context)
#
#     @classmethod
#     def post(cls, request: HttpRequest, product_id):
#         cart = CartService(request)
#
#         product = get_object_or_404(Product, id=str(request.POST.get('option')))
#         quantity = int(request.POST.get('amount'))
#
#         if quantity < 1:
#             quantity = 1
#         if int(product_id) == product.id:
#             cart.add_to_cart(product, quantity, update_quantity=True)
#         else:
#             cart.update_product(product, quantity, product_id)
#
#         return redirect('cart_detail')
#
# class CartAdd(View):
#     """
#     Добавление позиций в корзине
#     ::Страница: Корзина
#     """
#     def get(self, request: HttpRequest, product_id: int):
#         cart = CartService(request)
#         product = get_object_or_404(Product, id=str(product_id))
#         cart.add_to_cart(product, quantity=1, update_quantity=False)
#         return redirect(request.META.get('HTTP_REFERER'))
#
#     def post(self, request: HttpRequest, product_id: int):
#         cart = CartService(request)
#         product = get_object_or_404(Product, id=str(product_id))
#         quantity = int(request.POST.get('quantity'))
#         added = cart.add_to_cart(product, quantity=quantity, update_quantity=False)
#         if added:
#             messages.add_message(request, settings.SUCCESS_ADD_TO_CART, _(f'{product.name} был успешно добавлен в корзину.'))
#         else:
#             messages.add_message(request, settings.ERROR_ADD_TO_CART, _(f'Не удалось добавить {product.name}.Возможно не достаточно на складе.'))
#         return redirect(request.META.get('HTTP_REFERER'))
#
# class CartRemove(View):
#     """
#     Удаление позиции из корзины
#     ::Страница: Корзина
#     """
#     def get(self, request: HttpRequest, product_id: int):
#         cart = CartService(request)
#         cart.remove_from_cart(product_id)
#         return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


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