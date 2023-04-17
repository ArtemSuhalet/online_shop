from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name="frontend/index.html")),
    path('about/', TemplateView.as_view(template_name="frontend/about.html")),
    path('account/', TemplateView.as_view(template_name="frontend/account.html")),
    path('cart/', TemplateView.as_view(template_name="frontend/cart.html")),
    path('catalog/', TemplateView.as_view(template_name="frontend/catalog.html")),
    path('catalog/<int:pk>', TemplateView.as_view(template_name="frontend/catalog.html")),
    path('history-order/', TemplateView.as_view(template_name="frontend/order_list.html")),
    path('order-detail/<int:pk>', TemplateView.as_view(template_name="frontend/history_detail.html")),
    path('order/', TemplateView.as_view(template_name="frontend/order.html")),
    path('payment/', TemplateView.as_view(template_name="frontend/paymentcard.html")),
    path('payment-someone/', TemplateView.as_view(template_name="frontend/paymentaccount.html")),
    path('product/<int:pk>', TemplateView.as_view(template_name="frontend/product.html")),
    path('profile/', TemplateView.as_view(template_name="frontend/profile.html")),
    path('progress-payment/', TemplateView.as_view(template_name="frontend/payment_process.html")),
    path('sale/', TemplateView.as_view(template_name="frontend/sale.html")),
]
