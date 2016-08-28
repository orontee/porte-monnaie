"""The settings file used by the live production server.

"""

import os
import os.path
from django.contrib.messages import constants as messages
from purse.settings.base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'porte-monnaie_data',
        'USER': 'porte-monnaie',
        'PASSWORD': '',
        'HOST': os.environ['DJANGO_DATABASE_HOST'],
        'PORT': '',
        'CONN_MAX_AGE': 600,
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.cached.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        },
    },
]

ALLOWED_HOSTS = ['*']

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

STATIC_ROOT = os.path.join(PROJECT_PATH, 'public/static/')

EMAIL_HOST = os.environ['EMAIL_HOST']
SERVER_EMAIL = os.environ['DJANGO_ADMIN_EMAIL']
DEFAULT_FROM_EMAIL = SERVER_EMAIL

MESSAGE_LEVEL = messages.INFO
