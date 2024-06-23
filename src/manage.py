#!/usr/bin/env python
from decouple import config
import os
import sys

if __name__ == '__main__':
    if config("DEBUG", cast=bool, default=True):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yabpt.settings.development")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yabpt.settings.production")
        
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
