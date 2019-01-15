"""
Django settings for ontask project.

Generated by 'django-admin startproject' using Django 1.11.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

import mongoengine

if os.environ.get('ONTASK_DEVELOPMENT') is not None:
    from config.dev import *
    DEBUG = True
    CELERY_BROKER_URL = 'amqp://rabbitmq'
    FRONTEND_DOMAIN = 'https://localhost:3000' # For whitelisting CORS and authentication
    BACKEND_DOMAIN = 'https://localhost:8000'
    ALLOWED_HOSTS = ['localhost']
    SQL_DATABASE = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ontask',
        'USER': 'ontask',
        'PASSWORD': 'ontask',
        'HOST': 'sql',
        'PORT': '5432'
    }
    NOSQL_DATABASE = {
        'HOST': 'nosql',
        'DB': 'ontask'
    }

elif os.environ.get('ONTASK_DEMO') is not None:
    from config.demo import *

else:
    from config.prod import *

AWS_PROFILE = None

LTI_URL = LTI_CONFIG.get('url')
if LTI_URL:
    X_FRAME_OPTIONS = f'ALLOW-FROM {LTI_URL}'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_mongoengine',
    'authtools',
    'accounts',
    'scheduler',
    'corsheaders'
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

CORS_ORIGIN_WHITELIST = (
    FRONTEND_DOMAIN # Domain specified in the config file
)

ROOT_URLCONF = 'ontask.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'ontask.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': SQL_DATABASE
}

mongoengine.connect(NOSQL_DATABASE['DB'], host=NOSQL_DATABASE['HOST'])

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    )
}

AUTH_USER_MODEL = 'authtools.User'

# Default celery broker 
# http://docs.celeryproject.org/en/latest/getting-started/brokers/rabbitmq.html

CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True
TIME_ZONE = 'UTC'

# Workaround for "BrokenPipeError: [Errno 32] Broken pipe" issue with Celery
# Refer to https://github.com/celery/celery/issues/4226
BROKER_POOL_LIMIT = 0

DB_DRIVER_MAPPING = {
    "postgresql": "postgresql",
    "mysql":"mysql+pymysql"
}
