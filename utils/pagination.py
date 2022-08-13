from django.core.cache import cache
from django.core.paginator import Paginator
from django.utils.functional import cached_property

from rest_framework.pagination import PageNumberPagination

from utils.cache import WEEK


class CachedDjangoPaginator(Paginator):
    pagination_default_count = 1000

    @cached_property
    def count(self):
        # Internal Cache pagination
        cache_key = f"pagination:{self.object_list.model.__name__}"
        count = cache.get(cache_key, self.pagination_default_count)
        if count is not None:
            return count
        count = self.object_list.count()
        cache.set(cache_key, count, WEEK)
        return count


class CachedDjangoPagination(PageNumberPagination):
    django_paginator_class = CachedDjangoPaginator
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    pagination_default_count = 1000

    @cached_property
    def count(self):
        # Internal Cache pagination
        cache_key = f"pagination:api:{self.object_list.model.__name__}"
        count = cache.get(cache_key, self.pagination_default_count)
        if count is not None:
            return count
        count = self.object_list.count()
        cache.set(cache_key, count, WEEK)
        return count