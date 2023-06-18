import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '<django_package_name>.settings.development')

application = get_wsgi_application()
