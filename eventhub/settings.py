import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent             # project (where manage.py & db)
APP_ROOT = Path(os.path.dirname(__file__))                    # application (where settings.py & other configs)
sys.path.insert(0, os.path.join(APP_ROOT, 'apps'))            # subapps (backend) of the main eventhub application

load_dotenv()

# development settings
# TODO: review before prod
# keep the secret key used in production secret
SECRET_KEY = 'django-insecure-xll-_^stt^ayck7ys1cq=ui5v7qnz&k8#)j0)-)n8^5+ar)(_6'
DEBUG = True         # disable on prod
ALLOWED_HOSTS = []
WSGI_APPLICATION = 'eventhub.wsgi.application'


# Application definition
ROOT_URLCONF = 'eventhub.urls'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'core'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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
            ],
        },
    },
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [ APP_ROOT / "static" ]

# TODO: for prod run python manage.py collectstatic
STATIC_ROOT = BASE_DIR / "staticfiles"

# media
UPLOADCARE = {
    "pub_key": os.getenv('UPLOADCARE_PUBLIC_KEY'),
    "secret": os.getenv('UPLOADCARE_SECRET'),
}
CDN_DOMAIN = os.getenv('CDN_DOMAIN')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.Profile' # custom user model

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
