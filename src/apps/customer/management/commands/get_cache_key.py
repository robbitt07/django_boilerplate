from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = "Get a cache key"

    def add_arguments(self, parser):
        parser.add_argument("key", type=str)

    def handle(self, *args, **kwargs):
        key = kwargs["key"]
        result = cache.get(key)
        self.stdout.write(f"Cache for key: `{key}` | result: {result}\n")