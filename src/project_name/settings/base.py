from decouple import config
from django.core.management.utils import get_random_secret_key
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE_DIR = os.path.dirname(BASE_DIR)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", cast=str)
DEBUG = config('DEBUG', cast=bool, default=True)
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')], default='*'
)
ENV = config('ENV', cast=str)

PREREQUISITES_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

PROJECT_APPS = [
    'apps.appadmin',
    'apps.customer',
]

THIRD_PARTY_APPS = [
    'corsheaders',
    'crispy_forms',
    'rest_framework',
]

INSTALLED_APPS = PREREQUISITES_APPS + PROJECT_APPS + THIRD_PARTY_APPS

# User model
AUTH_USER_MODEL = "customer.User"

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGIN_URL = '/login/'
LOGIN_EXEMPT_URLS = ['/static/',] # Requires list of strings

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Custom Middleware
    'utils.middleware.LoginRequiredMiddleware',
    'utils.middleware.UserCustomerMiddleware', # Attach Customer, Permissions, Config
]

ROOT_URLCONF = '<django_package_name>.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(os.path.dirname(BASE_DIR), 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = '<django_package_name>.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static and Asset Files
USE_REMOTE_FILE_SYSTEM = config('USE_REMOTE_FILE_SYSTEM', cast=bool, default=False)
if USE_REMOTE_FILE_SYSTEM:
    # Cloud File Storage
    STATICFILES_DIRS = [
        os.path.join(PACKAGE_DIR, 'staticfiles'),
    ]

    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', cast=str)
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', cast=str)
    AWS_DEFAULT_ACL = None
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', cast=str)
    AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL', cast=str)

    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }

    AWS_LOCATION = config('AWS_LOCATION', cast=str)
    STATIC_URL = f"https://{AWS_S3_ENDPOINT_URL}/{AWS_LOCATION}/"

    # Static Files (CSS, JS, Images)
    AWS_STATIC_LOCATION = f'{AWS_LOCATION}/static'
    STATICFILES_STORAGE = 'utils.storage_backends.StaticStorage'

    # Public Media Files (PDF for content)
    AWS_PUBLIC_MEDIA_LOCATION = f'{AWS_LOCATION}/media/public'
    DEFAULT_FILE_STORAGE = 'utils.storage_backends.PublicMediaStorage'

    # Private Media Files (Customer Files, Load History, etc)
    AWS_PRIVATE_MEDIA_LOCATION = f'{AWS_LOCATION}/media/private'
    PRIVATE_FILE_STORAGE = 'utils.storage_backends.PrivateMediaStorage'

else:
    # Local File Storage
    # Static files (CSS, JavaScript, Images)
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [
        os.path.join(PACKAGE_DIR, 'staticfiles'),
    ]
    STATIC_ROOT = os.path.join(PACKAGE_DIR, 'static-cdn-local')

    # Media Files
    MEDIA_ROOT = os.path.join(PACKAGE_DIR, 'media')
    MEDIA_URL = '/media/'


# Cache
REDIS_CONN_STR = config('REDIS_CONN_STR', cast=str, default='')
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_CONN_STR,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,  # seconds
            "SOCKET_TIMEOUT": 5,  # seconds
        },
        "KEY_PREFIX": "<django_package_name>"
    }
}

# RabbitMQ
RABBITMQ_HOST = config('RABBITMQ_HOST', cast=str, default='localhost')
RABBITMQ_PORT = config('RABBITMQ_PORT', cast=int, default=5672)
RABBITMQ_VHOST = config('RABBITMQ_VHOST', cast=str, default='webhookk')
RABBITMQ_USER = config('RABBITMQ_USER', cast=str, default='guest')
RABBITMQ_PASS = config('RABBITMQ_PASS', cast=str, default='guest')
RABBITMQ_QUEUES = []

# Logging
LOGGING_FORMATTERS = {
    'generic': {
        'format': '%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S',
        'class': 'logging.Formatter'
    },
}

LOGGING_HANDLERS = {
    'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'generic',
    },
    'api_file': {
        'formatter': 'generic',
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'filename': os.path.join(PACKAGE_DIR, 'logs', 'api.log'),
        'when': 'd',
        'interval': 1,
        'backupCount': 90
    },
    'sql_file': {
        'formatter': 'generic',
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'filename': os.path.join(PACKAGE_DIR, 'logs', 'sql.log'),
        'when': 'd',
        'interval': 1,
        'backupCount': 90
    },
    'service_file': {
        'formatter': 'generic',
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'filename': os.path.join(PACKAGE_DIR, 'logs', 'service.log'),
        'when': 'd',
        'interval': 1,
        'backupCount': 90
    },
    'task_file': {
        'formatter': 'generic',
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'filename': os.path.join(PACKAGE_DIR, 'logs', 'task.log'),
        'when': 'd',
        'interval': 1,
        'backupCount': 90
    },
}

LOGGING_LOGGERS = {
    'api': {
        'level': 'DEBUG',
        'handlers': ['console', 'api_file'],
    },
    'server.request': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    'service': {
        'level': 'DEBUG',
        'handlers': ['console', 'service_file'],
    },
    'task': {
        'level': 'DEBUG',
        'handlers': ['console', 'task_file'],
    },
}

# Customer Integration
CURRENT_CUSTOMER_INTEGRATION = "STRIPE"

# Stripe
STRIPE_SECRET_API_KEY = config('STRIPE_SECRET_API_KEY', cast=str)
STRIPE_WEBHOOK_API_KEY = config('STRIPE_WEBHOOK_API_KEY', cast=str)