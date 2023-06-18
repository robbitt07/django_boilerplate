from django.db.models import Q

from functools import reduce
import operator
from typing import Dict

def base_transform(x): return x


class ListFilterMixin:
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
	order_by_ls = []

	def get_order_by_ls(self):
		return self.order_by_ls or []

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

	def parse_query_params(self):
		# Get Default Parameters
		raw_query_dict = self.get_default_params().copy()
		
		# Update with Passed Parameters
		raw_query_dict.update(self.request.GET.dict())

		filter_params_map = self.get_filter_params_map()
		filter_params_transform = self.get_filter_params_transform()

		# TODO: Update to using standard query param cleaning
		raw_query_dict = {
			key: value for key, value in raw_query_dict.items()
			if key in filter_params_map and value != ''
		}

		# Apply Param Routing and Transformation Logic
		filter_ls = [
			Q(reduce(operator.or_, [
				Q(**{field: filter_params_transform.get(field, base_transform)(value)})
				for field in filter_params_map.get(param, [param])
			]))
			for param, value in raw_query_dict.items()
		]
		filter_args = self.get_filter_args()
		return filter_ls, filter_args

	def get_extra_query_params(self,*args,**kwargs):
		return {}

	def get_annotations(self, *args, **kwargs) -> Dict:
		return {}

	def get_exclusions(self):
		return []
	
	def get_base_queryset(self):
		return super().get_queryset()

	def get_queryset(self):
		filter_ls, filter_args = self.parse_query_params()
		extra_query_params = self.get_extra_query_params()
		annotations = self.get_annotations()

		# Define base queryset
		qs = self.get_base_queryset().annotate(
			**annotations
		).filter(
			*filter_args, *filter_ls, **extra_query_params
		)

		# Exclusions
		for exclusion in self.get_exclusions():
			qs = qs.exclude(**exclusion)

		# Order By Logic -> TODO: Have field level order by
		qs = qs.order_by(*self.get_order_by_ls())
		return qs

