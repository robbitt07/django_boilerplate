from django.core.cache import cache

from typing import Dict

# Cache items
MINUTE = 60
HOUR = MINUTE*60
DAY = HOUR*24
WEEK = DAY*7
MONTH = DAY*30


def get_user_state(request, state_key):
    return cache.get(f'{request.user.pk}:state:{state_key}', None)


def set_user_state(request, state_key, obj):
    cache.set(f'{request.user.pk}:state:{state_key}', obj, DAY*5)


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
    
    class CachedUserSerializer(object):
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

    def __init__(self, id: int = None, instance: object = None, context: Dict = None, *args, **kwargs) -> None:
        self.id = id
        self.instance = instance
        self.context = context
        assert self.id is not None or self.instance is not None, "Must provide id or instance"
        assert self.model_class is not None and self.serializer_class is not None, "Improperly configured"

        # Update Model Name if only class provided
        if self.model_name is None:
            self.model_name = self.model_class.__name__.lower()

        # Get ID if Object Passed
        if self.id is None and self.instance is not None:
            self.id = self.instance.pk

    @property
    def data(self):
        # `cached_obj`:<obj_name>:<id>:<serialized_type>`
        cache_key = f"cached_obj:{self.model_name}:{self.id}:{self.serializer_name}"

        # Get Cache or Update
        result = cache.get(cache_key, None)

        # Get Update
        if result is None:
            if self.instance is None:
                self.instance = self.model_class.objects.get(pk=self.id)
            result = self.serializer_class(
                self.instance, context=self.context
            ).data
            cache.set(cache_key, result, self.duration)

        return result
