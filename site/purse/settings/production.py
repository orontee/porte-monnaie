"""The settings file used by the live production server. 
"""

from purse.settings.base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'porte-monnaie_data',
        'USER': 'porte-monnaie',
        'PASSWORD': '',
        'HOST': 'postgresql1.alwaysdata.com', 
        'PORT': '',
    }
}

ALLOWED_HOSTS = ['*']

STATIC_ROOT = os.path.join(PROJECT_PATH, '/public/static/')
