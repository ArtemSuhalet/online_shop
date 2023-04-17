from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from my_store_app.models import *
from django.utils.translation import gettext_lazy as _

# class SalesAdmin(admin.ModelAdmin):
#     list_display = ['product', 'shop', 'count', 'dateFrom', 'dateTo']
#     search_fields = ['product']

@admin.register(Profile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['email']
    search_fields = ['email']

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'image']
    search_fields = ['name']

class SpecificationsInline(admin.TabularInline):
    model = Specifications

class CommentsInline(admin.TabularInline):
    model = ProductComment

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'is_published', 'limited', 'get_tags', 'price', 'quantity', 'slug', 'rating']
    search_fields = ['name', 'category']

    inlines = [SpecificationsInline, CommentsInline]


    def get_tags(self, obj):
        lst_tags = []
        for item in obj.tags.all().values('name'):
            lst_tags.append(str(item['name']))
        return ", ".join(lst_tags)



    get_tags.short_description = _('tags')

    actions = ['mark_published', 'mark_unpublished', 'mark_male_limited', 'mark_del_limited']


    def mark_published(self, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(is_published=True)


    def mark_unpublished(self, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(is_published=False)


    def mark_male_limited(self, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(limited=True)


    def mark_del_limited(self, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(limited=False)


    mark_published.short_description = _('Publish')
    mark_unpublished.short_description = _('Remove from publication')
    mark_male_limited.short_description = _('Make products as limited')
    mark_del_limited.short_description = _('Cancel limited status for products ')

@admin.register(ProductComment)
class ProductComment(admin.ModelAdmin):
    list_display = ('author', 'content', 'added')
    list_filter = ('author', 'added')
    search_fields = ('author', 'added')

    actions = ['delete_text']

    def delete_text(self, request, queryset):
        queryset.update(content=_('[removed by admin]'))

    def get_text_comment(self, obj):
        return ''.join([obj.content[:15], "..."])

    get_text_comment.short_description = _('text comment')
    delete_text.short_description = _('delete text comment')

@admin.register(Specifications)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ['value', 'product']


class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ['user_order', 'product_order', 'payment_date',
                    'delivery_type', 'payment_type', 'total_cost', 'status', 'city', 'address']
    search_fields = ['user_order']


# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['product_order', 'count', 'total_price',
#                     'date', 'free_delivery']
#     search_fields = ['product_order']


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer', 'phone', 'email', 'payment_method',
                    'in_order', 'paid', 'ordered', 'delivery_cost')
    list_filter = ['paid', 'ordered']
    inlines = [OrderProductInline]



class PaymentAdmin(admin.ModelAdmin):
    list_display = ['number', 'name', 'month', 'year', 'code']
    search_fields = ['number']





admin.site.register(OrderHistory, OrderHistoryAdmin)

admin.site.register(Payment, PaymentAdmin)
