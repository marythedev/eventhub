import os
import sys
from decimal import Decimal
from pathlib import Path
import dj_database_url 

import environ

# ---------------------------------------
# App Paths
# ---------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent             # project (where manage.py & db)
APP_ROOT = Path(os.path.dirname(__file__))                    # application (where settings.py & other configs)
sys.path.insert(0, os.path.join(APP_ROOT, 'apps'))            # subapps (backend) of the main eventhub application


# ---------------------------------------
# Environmental Variables
# ---------------------------------------
env = environ.Env()
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    environ.Env.read_env(str(ENV_FILE))


# Security / Debug Settings
# TODO: review before prod
# keep the secret key used in production secret
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)         # disable on prod
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
WSGI_APPLICATION = 'eventhub.wsgi.application'


# Basic Settings
DOMAIN_URL = env("DOMAIN_URL", default=None)
SESSION_EXPIRY_TIME = env.int("SESSION_EXPIRY_TIME", default=0)

DATABASE_URL = env("DATABASE_URL", default=None)

# Email
EMAIL_HOST_USER = env("SUPPORT_EMAIL", default=None)
EMAIL_HOST_PASSWORD = env("SUPPORT_EMAIL_APP_PASSWORD", default=None)

# Media Settings
UPLOADCARE = {
    "pub_key": env("UPLOADCARE_PUBLIC_KEY", default=None),
    "secret": env("UPLOADCARE_SECRET", default=None),
}
CDN_DOMAIN = env("CDN_DOMAIN", default=None)

MAX_UPLOAD_MB = env.int("MAX_UPLOAD_MB", default=5)
SUPPORTED_IMAGE_FORMATS = env.list("SUPPORTED_IMAGE_FORMATS", default=["JPEG", "PNG", "WEBP"])
AVATAR_IMAGE_DIMENSIONS = tuple(map(int, env.list("AVATAR_IMAGE_DIMENSIONS", default=["300", "300"])))
EVENT_IMAGE_SIZE_KB = env.int("EVENT_IMAGE_SIZE_KB", default=500)
EVENT_IMAGE_DIMENSION = env.int("EVENT_IMAGE_DIMENSION", default=1200)

# Recommendation System Scoring Settings
CATEGORY_SCORE = env.int("CATEGORY_SCORE", default=30)
LOCATION_SCORE = env.int("LOCATION_SCORE", default=40)
PRICE_MIN_MAX_MATCH_SCORE = env.int("PRICE_MIN_MAX_MATCH_SCORE", default=20)
PRICE_MAX_MATCH_SCORE = env.int("PRICE_MAX_MATCH_SCORE", default=10)
PURCHASED_SCORE = env.int("PURCHASED_SCORE", default=-1000)

# Checkout / Payment / Stripe Settings
RESERVED_TICKET_EXPIRATION_MIN = env.int("RESERVED_TICKET_EXPIRATION_MIN", default=10)
SERVICE_FEE = Decimal(env("SERVICE_FEE", default="0.08"))
STRIPE_PUBLIC_KEY = env("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY")


# ---------------------------------------
# Application definition
# ---------------------------------------
ROOT_URLCONF = 'eventhub.urls'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'core',
    'users',
    'events',
    'checkout.apps.CheckoutConfig',
    'tickets.apps.TicketsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LOGIN_URL = '/login/'


# ---------------------------------------
# Password validation
# ---------------------------------------
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



# ---------------------------------------
# Templates & Context Processors
# ---------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [APP_ROOT / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.file_upload_settings',
                'core.context_processors.fee_settings'
            ],
        },
    },
]


# ---------------------------------------
# Static files (CSS, JavaScript, Images)
# ---------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [ APP_ROOT / "static" ]

STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ---------------------------------------
# Database
# ---------------------------------------
DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600
    )
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.Profile' # custom user model


# ---------------------------------------
# Email configurations
# ---------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# ---------------------------------------
# Internationalization
# ---------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
