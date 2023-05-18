from my_store_app.services.cart import Cart

from my_store_app.models import SiteSettings


def cart(request):
    return {"cart": Cart(request)}


def load_settings(request):
    return {"site_settings": SiteSettings.load()}
