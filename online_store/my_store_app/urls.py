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
    #path('async_catalog/', AllCardForAjax.as_view(), name="ajax_full"),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product'),
    path('get_reviews/', get_reviews, name='get_reviews'),
    path('post_review/', post_review, name='post_review'),
    path('add_viewed/', add_viewed, name='add_viewed'),
    #корзина
    # path('cart/', CartView.as_view(), name='cart_detail'),
    # path('cart/<int:product_id>', CartView.as_view(), name='cart_detail_post'),
    # path('add/<int:product_id>/', CartAdd.as_view(), name='cart_add'),
    # path('add/<int:product_id>/', CartAdd.as_view(), name='cart_add_many'),
    # path('remove/<int:product_id>/', CartRemove.as_view(), name='cart_remove'),
    # path('clear/', cart_clear, name='cart_clear'),
    path('cart', cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', cart_add, name='cart_add'),
    path('remove/<int:product_id>/', cart_remove, name='cart_remove'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
