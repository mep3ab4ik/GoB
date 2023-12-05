# pylint: disable=too-many-lines
"""
Django settings for django_app project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

import sentry_sdk
from django.db.models import options
from sentry_sdk.integrations.django import DjangoIntegration
from split_settings.tools import include, optional

from utils.secrets import SecretsStorage

secrets = SecretsStorage(Path(os.environ.get('SECRETS_PATH', '')))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-*1ehn3+4efr7e@oo!@wy@78nbej9%-(fvl5h1&q5q^t)q^m=_p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

SHELL_PLUS = 'ipython'

# Application definition

INSTALLED_APPS = [
    # django defaults
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd party frameworks
    'drf_yasg',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'channels',
    'nested_inline',
    'django_filters',
    'nested_admin',
    'adminsortable2',
    'bootstrap',
    # my apps
    'app.apps.ApiConfig',
    'django_extensions',
    'django_json_widget',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'django_app.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'goons'),
        'USER': os.environ.get('DB_USER', 'goons'),
        'PASSWORD': secrets.get('DB_PASSWORD', os.environ.get('DB_PASSWORD', 'goons')),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', 5432),
    },
    'nonrel': {
        'ENGINE': 'djongo',
        'NAME': 'goons',
        'CLIENT': {
            'host': os.environ.get('MONGO_HOST', 'localhost'),
        },
        'TEST': {
            'MIRROR': 'default',
        },
    },
}
DATABASE_ROUTERS = ['django_app.db_router.NonRelRouter']
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('in_db',)

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'app.User'

STATIC_ROOT = os.environ.get('STATIC_ROOT', BASE_DIR / 'static')

# cors settings
CORS_ORIGIN_WHITELIST = [
    'http://127.0.0.1',
    'http://localhost:3000',
    'https://localhost:3000',
    'https://dev-api.getagoon.com',
    'http://localhost',
    'http://localhost:4242',
    'http://127.0.0.1:3000',
]
CORS_ALLOW_CREDENTIALS = True
# CORS_EXPOSE_HEADERS = ['Set-Cookie']
# SESSION_COOKIE_SAMESITE = 'None'
# CSRF_COOKIE_SAMESITE = 'None'
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# SESSION_COOKIE_HTTPONLY = False
CORS_ORIGIN_ALLOW_ALL = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.TokenAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
}

# Configure media folder
MEDIA_ROOT = BASE_DIR / 'media'

# Channels
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = 6379
REDIS_HOST_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/1'
ASGI_APPLICATION = 'django_app.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_HOST_URL],
            'capacity': 2000,  # default 100
            'expiry': 60,  # default 60
        },
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_HOST_URL,
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
        'KEY_PREFIX': 'goons',
    }
}

ROOM_TICKET_TTL = 7200

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'info': {
            'format': '[{asctime} - {levelname} - {module} - {funcName} - {lineno}]:  {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'info',
        },
    },
    'loggers': {
        'django': {
            'handlers': [
                'console',
            ],
            'level': 'INFO',
            'propagate': True,
        },
        'uvicorn': {
            'handlers': [
                'console',
            ],
            'level': 'INFO',
        },
    },
}

OPENSEA_API_URL = 'https://api.opensea.io/api/v1'
INFURA_MAINNET_HTTP_PROVIDER = 'https://mainnet.infura.io/v3/c9223e5581f14e88bfdeecfb2e338b25'
GOONS_CONTRACT_ADDRESS = '0x8442DD3e5529063B43C69212d64D5ad67B726Ea6'
GOONS_METADATA_URL_BASE = 'https://goons-metadata.herokuapp.com/'
# IMPORTANT. This is required for serialization, has to be overridden in the local_settings file
SITE_BASE_URI = 'http://localhost:8000'
GOONS_CONTRACT_ABI = [
    {
        'inputs': [{'internalType': 'string', 'name': 'baseURI', 'type': 'string'}],
        'stateMutability': 'nonpayable',
        'type': 'constructor',
    },
    {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'owner',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'approved',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'uint256',
                'name': 'tokenId',
                'type': 'uint256',
            },
        ],
        'name': 'Approval',
        'type': 'event',
    },
    {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'owner',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'operator',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'bool',
                'name': 'approved',
                'type': 'bool',
            },
        ],
        'name': 'ApprovalForAll',
        'type': 'event',
    },
    {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'previousOwner',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'newOwner',
                'type': 'address',
            },
        ],
        'name': 'OwnershipTransferred',
        'type': 'event',
    },
    {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'from',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'to',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'uint256',
                'name': 'tokenId',
                'type': 'uint256',
            },
        ],
        'name': 'Transfer',
        'type': 'event',
    },
    {
        'inputs': [],
        'name': 'GOONS_PROVENANCE',
        'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'MAX_GOONS',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'MAX_PRESALE',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [
            {'internalType': 'address', 'name': 'to', 'type': 'address'},
            {'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'},
        ],
        'name': 'approve',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [{'internalType': 'address', 'name': 'owner', 'type': 'address'}],
        'name': 'balanceOf',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'baseURI',
        'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [{'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}],
        'name': 'getApproved',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'goonsPrice',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'hasPresaleStarted',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'hasSaleStarted',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [
            {'internalType': 'address', 'name': 'owner', 'type': 'address'},
            {'internalType': 'address', 'name': 'operator', 'type': 'address'},
        ],
        'name': 'isApprovedForAll',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [{'internalType': 'uint256', 'name': 'numGoons', 'type': 'uint256'}],
        'name': 'mintGiveawayGoons',
        'outputs': [],
        'stateMutability': 'payable',
        'type': 'function',
    },
    {
        'inputs': [{'internalType': 'uint256', 'name': 'numGoons', 'type': 'uint256'}],
        'name': 'mintGoon',
        'outputs': [],
        'stateMutability': 'payable',
        'type': 'function',
    },
    {
        'inputs': [{'internalType': 'uint256', 'name': 'numGoons', 'type': 'uint256'}],
        'name': 'mintPresaleGoon',
        'outputs': [],
        'stateMutability': 'payable',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'name',
        'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'owner',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [{'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}],
        'name': 'ownerOf',
        'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'pausePresale',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'pauseSale',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'renounceOwnership',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [
            {'internalType': 'address', 'name': 'from', 'type': 'address'},
            {'internalType': 'address', 'name': 'to', 'type': 'address'},
            {'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'},
        ],
        'name': 'safeTransferFrom',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [
            {'internalType': 'address', 'name': 'from', 'type': 'address'},
            {'internalType': 'address', 'name': 'to', 'type': 'address'},
            {'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'},
            {'internalType': 'bytes', 'name': '_data', 'type': 'bytes'},
        ],
        'name': 'safeTransferFrom',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [
            {'internalType': 'address', 'name': 'operator', 'type': 'address'},
            {'internalType': 'bool', 'name': 'approved', 'type': 'bool'},
        ],
        'name': 'setApprovalForAll',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [{'internalType': 'string', 'name': 'baseURI', 'type': 'string'}],
        'name': 'setBaseURI',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [{'internalType': 'string', 'name': '_hash', 'type': 'string'}],
        'name': 'setProvenanceHash',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'startPresale',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'startSale',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [{'internalType': 'bytes4', 'name': 'interfaceId', 'type': 'bytes4'}],
        'name': 'supportsInterface',
        'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'symbol',
        'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [{'internalType': 'uint256', 'name': 'index', 'type': 'uint256'}],
        'name': 'tokenByIndex',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [
            {'internalType': 'address', 'name': 'owner', 'type': 'address'},
            {'internalType': 'uint256', 'name': 'index', 'type': 'uint256'},
        ],
        'name': 'tokenOfOwnerByIndex',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [{'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}],
        'name': 'tokenURI',
        'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [{'internalType': 'address', 'name': '_owner', 'type': 'address'}],
        'name': 'tokensOfOwner',
        'outputs': [{'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'totalSupply',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    {
        'inputs': [
            {'internalType': 'address', 'name': 'from', 'type': 'address'},
            {'internalType': 'address', 'name': 'to', 'type': 'address'},
            {'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'},
        ],
        'name': 'transferFrom',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [{'internalType': 'address', 'name': 'newOwner', 'type': 'address'}],
        'name': 'transferOwnership',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'withdraw',
        'outputs': [],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
]

NODE_IMX_PROJECT_PORT = 6060

# test email settings
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'goonstestemail@gmail.com'
EMAIL_HOST_PASSWORD = 'vyc1are2pwm!daf7ZGC'

# Prod email settings
# EMAIL_HOST_USER = 'noreply@getagoon.com'
# EMAIL_HOST_PASSWORD = 'G00n3ry!nc'

EMAIL_PORT = 587

PROJECT_NAME = 'Goons of Balatroon API'

API_INFO = {
    'title': PROJECT_NAME,
    'description': 'API for Goons of Balatroon Project',
}

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'LOGIN_URL': '/admin/login/',
    'LOGOUT_URL': '/admin/logout/',
    'SECURITY_DEFINITIONS': {'Token': {'type': 'apiKey', 'name': 'Authorization', 'in': 'header'}},
}


def load_option_from_env(option, default=False):
    return bool(int(os.environ.get(option, default)))


BOOTSTRAP_ENABLED = load_option_from_env('BOOTSTRAP_ENABLED', False)
BOOTSTRAP_PRUNE = load_option_from_env('BOOTSTRAP_PRUNE', False)
BOOTSTRAP_LOGS = True
BOOTSTRAP_LOGS_MODELS = True
BOOTSTRAP_LOGS_OBJECTS = False
BOOTSTRAP_LOGS_FIELDS = False
BOOTSTRAP_LANGUAGE = 'en'

AWS_ACCESS_KEY_ID = 'AKIAU3E4LJP6QND27JOI'  # dev s3 access
AWS_SECRET_ACCESS_KEY = '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'

AWS_STORAGE_BUCKET_NAME = 'goons-game-test'
AWS_CLOUDFRONT_DOMAIN = 'd31sk0d42o7nly.cloudfront.net'
MEDIA_FILES_LOCATION = 'media'
MEDIA_URL = f'//{AWS_CLOUDFRONT_DOMAIN}/{MEDIA_FILES_LOCATION}/'
DEFAULT_FILE_STORAGE = 'app.storage_backends.MediaStorage'

CLIENT_VERSION_CONFIG_BUCKET_NAME = 'goons-game-test'
CLIENT_VERSION_CONFIG_FILE_NAME = 'currentGameClientVersion.json'

MAX_HAND_CARD = 2

CELERY_CACHE_BACKEND = 'default'
CELERY_RESULT_BACKEND = REDIS_HOST_URL
CELERY_BROKER_URL = REDIS_HOST_URL

BATTLE_RECONNECT_GRACE_PERIOD = 60
BATTLE_TURN_LIMIT_SECONDS = 75
BATTLE_START_COUNTDOWN_SECONDS = 5
PING_SLEEP_TIME = 5
ALLOW_ANY_DECK = os.environ.get('ALLOW_ANY_DECK', False)

BACKEND_VERSION = 0.19
MAIN_API_URL = 'https://main-api-prod.herokuapp.com/'

GLOBAL_STATISTICS_DEFAULT_CACHE_TIME = 60
PLAYER_STATISTICS_DEFAULT_CACHE_TIME = 60
BATTLE_CARD_ID_CACHE_TIME = 60 * 60
BATTLE_STATE_TTL = 60 * 60

SKILL_POINTS_ON_VICTORY = 2
SKILL_POINTS_ON_LOSS = -1


SENTRY_URL = secrets.get('SENTRY_URL') or os.environ.get('SENTRY_URL')

sentry_sdk.init(
    environment=os.environ.get('ENVIRONMENT', 'local'),
    dsn=SENTRY_URL,
    integrations=[
        DjangoIntegration(),
    ],
    max_breadcrumbs=100,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
    # By default the SDK will try to use the SENTRY_RELEASE
    # environment variable, or infer a git commit
    # SHA as release, however you may want to set
    # something more human-readable.
    # release="myapp@1.0.0",
)

LOBBY_CONSUMER_REDIS_GROUP_PREFIX = 'lobby'
BATTLE_CONSUMER_REDIS_GROUP_PREFIX = 'game-users'
BATTLE_STATE_REDIS_PREFIX = 'game-state'
BATTLE_RECONNECT_REDIS_PREFIX = 'reconnect_cache'
REDIS_GROUP_PREFIX = 'game-'

DISABLE_PING = os.environ.get('DISABLE_PING', False)

include(optional('local_settings.py'))  # should be at the end of the file
