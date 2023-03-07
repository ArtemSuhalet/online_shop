from django.contrib import admin
from my_store_app.models import *


class SalesAdmin(admin.ModelAdmin):
    list_display = ['product', 'shop', 'count', 'dateFrom', 'dateTo']
    search_fields = ['product']


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['email']
    search_fields = ['email']


class CategoryProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'image']
    search_fields = ['title']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['category', 'specifications', 'price', 'count', 'date',
                    'title', 'description', 'rating', 'reviews']

    search_fields = ['title']


class TagsAdmin(admin.ModelAdmin):
    list_display = ['tags_name']
    search_fields = ['tags_name']


class ReviewsAdmin(admin.ModelAdmin):
    list_display = ['text', 'product', 'author', 'create_at']
    search_fields = ['author']


class SpecificationsAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']
    search_fields = ['name']


class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ['user_order', 'product_order', 'payment_date',
                    'delivery_type', 'payment_type', 'total_cost', 'status', 'city', 'address']
    search_fields = ['user_order']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['product_order', 'count', 'price',
                    'date', 'free_delivery']
    search_fields = ['product_order']


class BasketAdmin(admin.ModelAdmin):
    list_display = ['username', 'create_at']
    search_fields = ['username']


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['number', 'name', 'month', 'year', 'code']
    search_fields = ['number']


class ShopAdmin(admin.ModelAdmin):
    list_display = ['shop_name']
    search_fields = ['shop_name']


admin.site.register(Profile, UserProfileAdmin)
admin.site.register(CategoryProduct, CategoryProductAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Basket, BasketAdmin)
admin.site.register(Reviews, ReviewsAdmin)
admin.site.register(TagsFile, TagsAdmin)
admin.site.register(Specifications, SpecificationsAdmin)
admin.site.register(OrderHistory, OrderHistoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Sales, SalesAdmin)