"""The settings file used by the live production server.

"""

import os
import os.path
from django.contrib.messages import constants as messages
from purse.settings.base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'porte-monnaie_data',
        'USER': 'porte-monnaie',
        'PASSWORD': '',
        'HOST': os.environ['DJANGO_DATABASE_HOST'],
        'PORT': '',
    }
}

ALLOWED_HOSTS = ['*']

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

STATIC_ROOT = os.path.join(PROJECT_PATH, 'public/static/')

EMAIL_HOST = os.environ['EMAIL_HOST']
SERVER_EMAIL = os.environ['DJANGO_ADMIN_EMAIL']
DEFAULT_FROM_EMAIL = SERVER_EMAIL

MESSAGE_LEVEL = messages.INFO
