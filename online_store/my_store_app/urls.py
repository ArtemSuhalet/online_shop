from django.contrib import admin
from django.template.defaulttags import url
from django.urls import include, path
from my_store_app.views import *
from django.conf import settings
from django.conf.urls.static import static

from my_store_app import views

urlpatterns = [
    path('', CategoryView.as_view(), name='index'),
    path('register/', register_view, name='register'),
    path('logout/', AuthorLogoutView.as_view(), name='logout'),
    path('login/', Login.as_view(template_name='login.html'), name='login'),
    path('account/', account_view, name='account'),
    path('profile/', UserEditFormView.as_view(), name='profile'),
    path('catalog/', FullCatalogView.as_view(), name="catalog_url"),
    path('catalog/<tag_slug>/', tags, name='catalog_by_tag'),
    path('post/', post, name='post'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product'),
    path('get_reviews/', get_reviews, name='get_reviews'),
    path('post_review/', post_review, name='post_review'),
    path('search/', Search.as_view(), name='search'),
    path('add_viewed/', add_viewed, name='add_viewed'),
    #корзина
    path('cart', cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', cart_add, name='cart_add'),
    path('remove/<int:product_id>/', cart_remove, name='cart_remove'),
    #оформление заказа

    path('step1/', orderstepone, name='order_step_one'),
    path('step11/', OrderStepOneAnonym.as_view(), name='order_step_one_anonymous'),
    path('step2/<int:order_id>/', ordersteptwo, name='order_step_two'),
    path('step3/<int:order_id>/', OrderStepThree.as_view(), name='order_step_three'),
    path('step4/<int:order_id>/', OrderStepFour.as_view(), name='order_step_four'),
    # оплата
    path('payment/<int:order_id>/', PaymentView.as_view(), name='payment'),
    path('paymentcard/<int:order_id>/', PaymentWithCardView.as_view(), name='payment_with_card'),
    path('paymentaccount/<int:order_id>/', PaymentWithAccountView.as_view(), name='payment_with_account'),
    path('done/', payment_done, name='payment_done'),
    path('payment_process/<int:order_id>/', payment_process, name='payment_process'),
    path('canceled/', payment_canceled, name='payment_canceled'),
    #history
    path('order_list/', HistoryOrderView.as_view(), name='order_list'),
    path('history_detail/<int:order_id>', HistoryOrderDetail.as_view(), name='history_detail'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
