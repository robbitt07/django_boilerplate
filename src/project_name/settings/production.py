from .base import *
import datetime
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'CONN_MAX_AGE': 60,
        'OPTIONS': eval(config('DB_OPTIONS', '{}'))
    },
}


# CORS AND REST API
CORS_URLS_REGEX = r'.*/api/.*'
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    'https://<domain>',
)


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DATE_INPUT_FORMATS': (
        'iso-8601',
        'iso',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%f'
        '%Y-%m-%dT%H:%M:%S.%f%Z',
    ),
    'DATETIME_INPUT_FORMATS': (
        'iso-8601',
        'iso',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S.%f%Z',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
}

JWT_AUTH = {
    # how long the original token is valid for
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=2),

    # allow refreshing of tokens
    'JWT_ALLOW_REFRESH': True,

    # this is the maximum time AFTER the token was issued that
    # it can be refreshed.  exprired tokens can't be refreshed.
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),

    'JWT_RESPONSE_PAYLOAD_HANDLER': 'utils.auth.jwt_response_handler'
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'generic': {
            'format': '%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'class': 'logging.Formatter'
        },
    },
    'handlers': {
        'api_file': {
            'formatter': 'generic',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(PACKAGE_DIR, 'logs', 'api.log'),
            'when': 'd',
            'interval': 1,
            'backupCount': 90
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
        'request_file': {
            'formatter': 'generic',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(PACKAGE_DIR, 'logs', 'request.log'),
            'when': 'd',
            'interval': 1,
            'backupCount': 5
        },
        'service_file': {
            'formatter': 'generic',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(PACKAGE_DIR, 'logs', 'service.log'),
            'when': 'd',
            'interval': 1,
            'backupCount': 5
        },
        'task_file': {
            'formatter': 'generic',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(PACKAGE_DIR, 'logs', 'task.log'),
            'when': 'd',
            'interval': 1,
            'backupCount': 5
        },
    },
    'loggers': {
        'api': {
            'level': 'DEBUG',
            'handlers': ['console', 'api_file'],
        },
        'django.server': {
            'handlers': ['request_file', 'console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'service': {
            'level': 'DEBUG',
            'handlers': ['console', 'service_file'],
        },
        'task': {
            'level': 'DEBUG',
            'handlers': ['console', 'task_file'],
        },
    },
}