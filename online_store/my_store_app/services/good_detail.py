from typing import Dict, List

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Avg, QuerySet
from django.http import HttpRequest
from my_store_app.models import *




class CurrentProduct:
    """
    Класс для работы с экземпляром Product
    Функции:
    get_product,
    get_specifications,
    get_tags,
    get_reviews,
    get_review_page(queryset, page),
    calculate_product_rating()
    """

    def __init__(self, **kwargs) -> None:
        if 'slug' in kwargs:
            self.product = Product.objects.get(slug=kwargs['slug'])
        elif 'instance' in kwargs:
            self.product = kwargs['instance']
        else:
            raise ValueError

    @property
    def get_product(self) -> Product:
        return self.product


    @property
    def get_specifications(self) -> QuerySet:
        """
        Метод для получения specifications
        """
        specifications_cache_key = 'specifications:{}'.format(self.product.id)
        specifications = cache.get(specifications_cache_key)
        if not specifications:
            specifications = self.product.specifications.all()
            cache.set(specifications_cache_key, specifications, 24 * 60 * 60)
        return specifications

    @property
    def get_tags(self) -> QuerySet:
        """
        Метод для получения tags product
        """
        tags_cache_key = 'tags:{}'.format(self.product.id)
        tags = cache.get(tags_cache_key)
        if not tags:
            tags = self.product.tags.all()
            cache.set(tags_cache_key, tags, 24 * 60 * 60)
        return tags

    @property
    def get_reviews(self) -> QuerySet:
        """
         Метод для получения reviews product
        """
        reviews_cache_key = 'reviews:{}'.format(self.product.id)
        reviews = cache.get(reviews_cache_key)
        if not reviews:
            reviews = self.product.product_comments.all()
            cache.set(reviews_cache_key, reviews, 2 * 6 * 1)
        return reviews

    @classmethod
    def get_review_page(cls, queryset: QuerySet, page: int) -> Dict:
        """
        Метод для передачи страницы reviews в шаблон. Возвращает dict с queryset reviews и данными для пагинации
        """
        reviews_count = queryset.count()
        reviews = queryset.values('author', 'content', 'added')
        paginator = Paginator(reviews, 3)
        page_obj = paginator.get_page(page)
        json_dict = {
            'comments': list(page_obj.object_list),
            'has_previous': None if page_obj.has_previous() is False
            else "previous",
            'previous_page_number': page_obj.number - 1,
            'num_pages': page_obj.paginator.num_pages,
            'number': page_obj.number,
            'has_next': None if page_obj.has_next() is False
            else "next",
            'next_page_number': page_obj.number + 1,
            'empty_pages': None if page_obj.paginator.num_pages < 2
            else "not_empty",
            'reviews_count': reviews_count,
            'media': settings.MEDIA_URL
        }
        return json_dict

    def update_product_rating(self) -> None:
        """
        Метод для калькуляции и обновления рейтинга, когда review добавлено
        """
        rating = ProductComment.objects.only('rating') \
            .filter(product_id=self.product.id) \
            .aggregate(Avg('rating'))['rating__avg']
        if rating:
            self.product.rating = round(float(rating), 0)
            self.product.save(update_fields=['rating'])

def context_pagination(request: HttpRequest, queryset: QuerySet, size_page: int = 3) -> Paginator:
    """
    Пагинация
    """
    paginator = Paginator(queryset, size_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj

