from django.core.cache import cache
from django.core.cache.backends.db import DatabaseCache
from django.db import connections
from django.utils.encoding import force_bytes

import base64
from functools import wraps
from hashlib import md5
from logging import getLogger
import json
import pickle
from typing import Any, Dict, List

logger = getLogger("service")


# Cache items
MINUTE = 60
HOUR = MINUTE*60
DAY = HOUR*24
WEEK = DAY*7
MONTH = DAY*30


def get_user_state(request, state_key):
	return cache.get(f"{request.user.pk}:state:{state_key}", None)


def set_user_state(request, state_key, obj):
	cache.set(f"{request.user.pk}:state:{state_key}", obj, DAY*5)


def delete_model_cache(model_name: str, id: int = None):
	""" Helper function to clear out keys for CachedSerializer"""
	prefix = f"cached_obj:{model_name}:"
	prefix = f"{prefix}{id}:*" if id is not None else f"{prefix}*"

	keys = cache.keys(prefix)
	for cache_key in keys:
		cache.delete(cache_key)


class CachedSerializer(object):
	"""
	Cached Serializer Object to fetch from cache or DB, ideal for slow chaning 
	objects.
	
	class CachedUserSerializer(CachedSerializer):
		model_name = "user"
		serializer_name = "detail"
		model_class = get_user_model()
		serializer_class = UserSerializer
	
	"""
	model_class = None
	serializer_class = None
	model_name = None
	serializer_name = "detail"
	duration = WEEK

	def __init__(self, id: int, context: Dict = {}, *args, **kwargs) -> None:
		self.id = id
		self.context = {
			key: value for key, value in context.items()
			if key not in {"request", "format", "view"}
		} or {}
		assert self.model_class is not None and self.serializer_class is not None, "Improperly configured"

		# Update Model Name if only class provided
		if self.model_name is None:
			self.model_name = self.model_class.__name__.lower()

	@property
	def data(self):
		if self.id is None:
			return None

		# `cached_obj`:<obj_name>:<id>:<serialized_type>:<context_hash>`
		cache_key = (
			f"cached_obj:{self.model_name}:{self.id}:{self.serializer_name}:{hash(frozenset(self.context)) if self.context else ""}"
		)

		# Get Cache or Update
		result = cache.get(cache_key, None)

		# Get Update
		if result is None:
			self.object = self.model_class.objects.get(pk=self.id)
			result = self.serializer_class(self.object, context=self.context).data
			cache.set(cache_key, result, self.duration)

		return result


def get_func_cache_key(func: callable,
                       kwargs: Dict,
                       kwarg_keys: List[str] = None) -> str:
	"""Get Function Cache Key from set of Function, Tenant, Kwargs,
	and configured Kwarg Keys.  To 

	Parameters
	----------
	func : callable
		Wrapped Function 
	kwargs : Dict
		Kwargs from Wrapped Function call
	kwarg_keys : List[str]
		Specified keys from Kwargs to convert into hash

	Returns
	-------
	cache_key : str
		Cache Key
	"""
	func_name = func.__name__
	if kwarg_keys is None:
		func_kwargs_hash = md5(json.dumps({
			key: kwargs.get(key) for key in kwarg_keys
		}).encode("utf-8")).hexdigest()

	else:
		func_kwargs_hash = md5(json.dumps({
			key: value for key, value in kwargs.items()
		}).encode("utf-8")).hexdigest()

	return f"func_cache:{func_name}:{func_kwargs_hash}", func_name


def func_cache(kwarg_keys: List[str], ttl: int = DAY):
	"""Function Caching Wrapper to Cache Results

	Parameters
	----------
	kwarg_keys : List[str]
		_description_
	ttl : int, optional
		_description_, by default WEEK
	"""

	def real_decorator(f: callable) -> Any:  # a wrapper for the function

		@wraps(f)
		def func(*args, **kwargs):  # the decorated function

			# Get Cache Key
			cache_key, func_name = get_func_cache_key(
				func=f, kwargs=kwargs, kwarg_keys=kwarg_keys
			)

			response = cache.get(cache_key)
			if response is not None:
				logger.info(f"Fetched func=`{func_name}` from cache, key={cache_key}")
				return response

			logger.info(f"Func Cache not found, func=`{func_name}` key={cache_key}")
			response = f(*args, **kwargs)
			cache.set(cache_key, response, ttl)
			return response

		return func

	return real_decorator


class DatabaseCacheExtended(DatabaseCache):
    def keys(self, query, default: Any = None, version: int = None):
        db = "default"
        table = connections[db].ops.quote_name(self._table)

        query_prefix = f"{self.key_prefix}:{self.version}:"
        query = f"{query_prefix}{query}".replace("*", "%")
        with connections[db].cursor() as cursor:
            cursor.execute("SELECT cache_key, value, expires FROM %s "
                           "WHERE cache_key LIKE %%s" % table, [query])
            rows = cursor.fetchall()

        if len(rows) < 1:
            return {}

        return_d = {}
        for row in rows:
            value_bytes = connections[db].ops.process_clob(row[1])
            value = pickle.loads(base64.b64decode(force_bytes(value_bytes)))
            return_d[row[0].replace(query_prefix, "")] = value

        return return_d
