"""The settings file used when working on the project locally.

"""

import os
import tempfile
from django.contrib.messages import constants as messages
from purse.settings.base import *


DEBUG = True

DEBUG_TOOLBAR = False

if DEBUG_TOOLBAR:
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
    cls = 'debug_toolbar.middleware.DebugToolbarMiddleware'
    MIDDLEWARE_CLASSES = ((cls,) + MIDDLEWARE_CLASSES)
    DEBUG_TOOLBAR_PATCH_SETTINGS = False

INTERNAL_IPS = ('127.0.0.1',)

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
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        },
    },
]

LOGGING.update({
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(tempfile.gettempdir(), 'purse.log')
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'purse': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG'
        }
    }
})

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MESSAGE_LEVEL = messages.DEBUG
