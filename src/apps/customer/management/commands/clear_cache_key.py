from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = "Removed a cache key"

    def add_arguments(self, parser):
        parser.add_argument("key", type=str)

    def handle(self, *args, **kwargs):
        key = kwargs["key"]
        result = cache.delete(key)
        self.stdout.write(f"Cleared cache for key: `{key}` | result: {result}\n")