from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Removed cache keys for prefix'

    def add_arguments(self, parser):
        parser.add_argument('key', type=str)

    def handle(self, *args, **kwargs):
        prefix = kwargs['key']
            
        keys = cache.keys(prefix)
        for cache_key in keys:
            cache.delete(cache_key)
        
        self.stdout.write(f'Cleared cache for keys: `{prefix}` | result: {len(keys)}\n')