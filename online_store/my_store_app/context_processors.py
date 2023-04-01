from my_store_app.services.cart import Cart


def cart(request):
    return {'cart': Cart(request)}