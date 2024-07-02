from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response

from utils.yahp.cache import WEEK

from functools import reduce
import json
import operator
from typing import Any, Callable, Dict


def base_transform(x): return x


class QueryParamsMixin:
	"""
	Parse Query Params to a Flat Key/Value Result for abstract Views
	"""
	default_params = {}
	filter_params_map = {}
	filter_params_transform = {}

	def get_filter_params_map(self):
		return self.filter_params_map or {}

	def get_filter_params_transform(self):
		return self.filter_params_transform or {}

	def get_default_params(self):
		return self.default_params or {}

	def get_request_params(self):
		return self.request.GET.dict()

	def parse_query_params(self):
		# Get Default Parameters
		query_dict = self.get_default_params().copy()

		filter_params_map = self.get_filter_params_map()
		filter_params_transform = self.get_filter_params_transform()

		# Update with Passed Parameters
		self.query_params = {
			key: value for key, value in self.get_request_params().items()
			if key in filter_params_map and value != ''
		}
		query_dict.update(self.query_params)

		# Apply Param Routing and Transformation Logic
		query_dict = {
			key: filter_params_transform.get(key, base_transform)(value)
			for key, value in query_dict.items()
		}

		return query_dict


class FilterMixin:
	"""
	filter_params_map = {
		'carrier_name': ['carrier_name__icontains', 'carrier_dba__icontains',],
        'mc_number': ['mc_number__icontains'],
	}
    filter_params_transform = {
		'phone': lambda x: PhoneNumber(x).formatted,
        'viewable': lambda x: parse_bool(x),
	}
	"""
	default_params = {}
	filter_params_map = {}
	filter_params_transform = {}
	ordering = []
	persist_filters = False

	# TODO: Add Initial/Dispatch for Django/API
	# def dispatch(self, *args, **kwargs):
	# 	self.query_params = {
	# 		key: value for key, value in self.get_request_params()
	# 		if key in filter_params_map and value != ''
	# 	}

	@property
	def filter_cache_key(self):
		return f"persist_filters:{self.request.user.pk}:{self.__class__.__name__.lower()}"

	def get_ordering(self):
		return self.ordering or []

	def get_filter_params_map(self):
		return self.filter_params_map or {}

	def get_filter_params_transform(self):
		return self.filter_params_transform or {}

	def get_default_params(self):
		return self.default_params or {}

	def get_filter_args(self):
		return []

	def get_filter_field_transform(self):
		"""
		Function to perform transforms on fields
		"""
		pass

	def get_request_params(self):
		params = self.request.GET.dict()

		if self.persist_filters:

			# Clear Cache if params aside from page exists
			if params and set(params.keys()) != {"page"}:
				cache.delete(self.filter_cache_key)
				cache.set(self.filter_cache_key, params)
				return params

			# Update with Cached Values
			params.update(cache.get(self.filter_cache_key, {}))

		return params

	def parse_query_params(self):
		# Get Default Parameters
		query_dict = self.get_default_params().copy()
		
		filter_params_map = self.get_filter_params_map()
		filter_params_transform = self.get_filter_params_transform()
		
		# Update with Passed Parameters
		self.query_params = {
			key: value for key, value in self.get_request_params().items()
			if key in filter_params_map and value != ''
		}
		query_dict.update(self.query_params)

		# Cache
		if self.persist_filters:
			cache.set(self.filter_cache_key, self.query_params, WEEK)

		# Apply Param Routing and Transformation Logic
		filter_ls = [
			Q(reduce(operator.or_, [
				Q(**{field: filter_params_transform.get(field, base_transform)(value)})
				for field in filter_params_map.get(param, [param])
			]))
			for param, value in query_dict.items()
		]
		filter_args = self.get_filter_args()
		return filter_ls, filter_args

	def get_extra_query_params(self, *args, **kwargs):
		return {}

	def get_annotations(self, *args, **kwargs) -> Dict:
		return {}

	def get_exclusions(self):
		return []

	def get_base_queryset(self):
		"""
		Base queryset that allows for app based querysets to be injected prior to
		filters
		"""
		return super().get_queryset()

	def get_queryset(self):
		filter_ls, filter_args = self.parse_query_params()
		extra_query_params = self.get_extra_query_params()
		annotations = self.get_annotations()

		# Define base queryset
		qs = self.get_base_queryset().annotate(
			**annotations
		)
		qs = qs.filter(
			*filter_args, *filter_ls, **extra_query_params
		)

		# Exclusions
		for exclusion in self.get_exclusions():
			qs = qs.exclude(**exclusion)

		# Order By Logic -> TODO: Have field level order by
		qs = qs.order_by(*self.get_ordering())

		return qs

	def get_context_data(self):
		context = super().get_context_data()
		context["query_params"] = self.query_params
		context["raw_query_params"] = json.dumps(self.query_params)
		return context


class DeactivateMixin:
	"""Deactivate Mixin"""
	deactivate_field = "deactivated_on"  # Default Logic to Update Deactivate Field to Current Datetime
	deactivate_func: Callable[[Any], Callable]  = None  # Additional Option to Pass Instance to Function

	def destroy(self, request, *args, **kwargs):
		instance = self.get_object()

		# Leverage Function is Available
		if self.deactivate_func is not None:
			self.deactivate_func()(instance=instance, user_obj=self.request.user)
		else:
			setattr(instance, self.deactivate_field, timezone.now())
			instance.save()

		return Response(status=status.HTTP_204_NO_CONTENT)
