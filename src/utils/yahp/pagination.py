from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models.sql.query import Query
from django.db.models.sql.where import WhereNode
from django.utils.functional import cached_property

from rest_framework.pagination import PageNumberPagination

from utils.yahp.cache import WEEK


def query_filter_key(query: Query):
	"""Helper function to key Queryset Filter Key to Cache"""
	return f"|{query.where.connector}|".join([get_child_filter(child) for child in query.where.children])


def get_child_filter(child: object) -> str:
	# Recursive add child filter
	if isinstance(child, WhereNode):
		return f"|{child.connector}|".join([get_child_filter(child) for child in child.children])
	if not hasattr(child, 'lhs'):
		return ""
	return f"{child.lhs.field.name}|{child.lookup_name}|{child.rhs}"


class CachedDjangoPaginator(Paginator):
	"""
	Internal Cached Paginator allows for caching query set count based on 
	filter conditions for slow changing datasets
	"""
	cache_duration = WEEK

	@cached_property
	def count(self):
		# Internal Cache pagination
		filter_key = query_filter_key(self.object_list.query)
		cache_key = f"pagination:{self.object_list.model.__name__}:{filter_key}"
		count = cache.get(cache_key)
		if count is not None:
			return count

		count = self.object_list.count()
		cache.set(cache_key, count, self.cache_duration)
		return count


class CachedDjangoPagination(PageNumberPagination):
	"""Django Cached Count Rest Paginator"""
	django_paginator_class = CachedDjangoPaginator
	page_size = 20
	page_size_query_param = 'page_size'
	max_page_size = 1000


class DjangoPagination(PageNumberPagination):
	"""Django Rest Paginator"""
	page_size = 20
	page_size_query_param = 'page_size'
	max_page_size = 1000