from django.urls import include, path
from admin_app.views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = "admin_app"

urlpatterns = [
    path("items_list/", ItemsListView.as_view(), name="items_list"),
    path("item_list/<int:pk>/", ItemDetailView.as_view(), name="item_detail"),
    path(
        "edit_product/<int:product_id>/",
        ItemEditFormView.as_view(),
        name="edit_product",
    ),
    path("create_item/", ItemCreateView.as_view(), name="create_item"),
    path("upload/", upload_files, name="upload"),
    path("admin_list", admin_view, name="admin_list"),
    path("categories_list/", CategoriesListView.as_view(), name="categories_list"),
    path("orders_list/", OrdersListView.as_view(), name="orders_list"),
    path("reviews_list/", ReviewsListView.as_view(), name="reviews_list"),
    path("users_list/", UsersListView.as_view(), name="users_list"),
]

if settings.DEBUG:
    urlpatterns.extend(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
