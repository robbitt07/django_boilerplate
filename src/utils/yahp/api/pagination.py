from rest_framework.pagination import PageNumberPagination

from utils.yahp.pagination import CachedDjangoPaginator


class CachedDjangoPagination(PageNumberPagination):
	"""Django Rest Paginator"""
	django_paginator_class = CachedDjangoPaginator
	page_size = 20
	page_size_query_param = "page_size"
	max_page_size = 100
