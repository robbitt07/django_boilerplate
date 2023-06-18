from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.sql.query import Query
from django.db.models.sql.where import WhereNode
from django.utils.functional import cached_property

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
	filter conditions for slow changing datasets such as Carrier Master List
	"""
	cache_duration = WEEK

	@cached_property
	def count(self):
		# Internal Cache pagination
		filter_key = query_filter_key(self.object_list.query)
		cache_key = f"pagination:{self.object_list.model.__name__}:{filter_key}"

		# Attempt to get cache key
		count = cache.get(cache_key)
		if count is not None:
			return count

		# Default to Pagination Count for pre-defined model
		if hasattr(self.object_list.model._meta, 'default_pagination_count'):
			count = min([
				value for key, value in self.object_list.model._meta.default_pagination_count.items() 
				if key in cache_key
			] or [0])
			# TODO: Attempt to perform background cache set
			if count != 0:
				return count

		# Else get the count and continue
		count = self.object_list.count()
		cache.set(cache_key, count, self.cache_duration)
		return count


def get_pagination_context(prefix, iterable, page_number, paginate_by):
	'''
	Usage:  For pagination outside of what is automatically included in ListView.  Pagination will use url parameters of the form '<prefix>_page' for pagination where <prefix> is the prefix vaiable passed.
	
	In the View:

		def get_context_data(self,*args,*kwargs):
			context = super().get_context_data(*args,**kwargs)
			paginator_context = get_pagination_context(
				prefix='<prefix>',
				iterable=<queryset/list/iterable>,
				page_number=self.request.GET.get('<prefix>_page'),
				paginate_by=<paginate by integer>,
			)
			context.update(paginator_context)
			return context
	
	In the Template, also available in context are '<prefix>_count' providing the total number of objects in paginated collection and '<prefix>_exists' indicating if there are any elements in the list:
		
		{% for obj in <prefix>_page_obj %}
			...
		{% endfor %}
		...
		{% if <prefix>_is_paginated %}
			<ul class="pagination justify-content-center mt-2">
				{% if <prefix>_page_obj.has_previous %}
					<li class="page-item">
						<a class="page-link" href="?<prefix>_page={{ <prefix>_page_obj.previous_page_number }}{% for key, value in request.GET.items %}{% if key != '<prefix>_page' %}&{{ key }}={{ value }}{% endif %}{% endfor %}">&laquo;</a>
					</li>
				{% else %}
					<li class="page-item disabled"><span class="page-link">&laquo;</span></li>
				{% endif %}
			{% for i in <prefix>_paginator.page_range %}
				{% if <prefix>_page_obj.number == i %}
					<li class="page-item active">
						<span class="page-link">{{ i }} <span class="sr-only">(current)</span></span>
					</li>
				{% elif <prefix>_page_obj.number|add:"-8" < i and i < <prefix>_page_obj.number|add:"8" %}
					<li>
						<a class="page-link" href="?<prefix>_page={{ i }}{% for key, value in request.GET.items %}{% if key != '<prefix>_page' %}&{{ key }}={{ value }}{% endif %}{% endfor %}">{{ i }}</a>
					</li>
				{% endif %}
			{% endfor %}
			{% if <prefix>_page_obj.has_next %}
				<li>
					<a class="page-link" href="?<prefix>_page={{ <prefix>_page_obj.next_page_number }}{% for key, value in request.GET.items %}{% if key != '<prefix>_page' %}&{{ key }}={{ value }}{% endif %}{% endfor %}">&raquo;</a>
				</li>
			{% else %}
				<li class="page-item disabled"><span class="page-link">&raquo;</span></li>
			{% endif %}
			</ul>
		{% endif %}

	'''
	count = len(iterable)
	paginator = Paginator(iterable, paginate_by)
	try:
		page_obj = paginator.page(page_number)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)
	if prefix is None:
		context = {
			f'paginator': paginator,
			f'page_obj': page_obj,
			f'is_paginated': count > paginate_by,
			f'count': count,
			f'exists': count > 0,
		}
	else:
		context = {
			f'{prefix}_paginator': paginator,
			f'{prefix}_page_obj': page_obj,
			f'{prefix}_is_paginated': count > paginate_by,
			f'{prefix}_count': count,
			f'{prefix}_exists': count > 0,
		}
	return context
