from django import template
from my_store_app.models import *



register = template.Library()

@register.simple_tag()
def get_categories():
    return ProductCategory.objects.all()