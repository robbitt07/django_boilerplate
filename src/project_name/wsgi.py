from decouple import config
import os

from django.core.wsgi import get_wsgi_application

if config("DEBUG", cast=bool, default=True):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yabpt.settings.development")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yabpt.settings.production")

application = get_wsgi_application()
