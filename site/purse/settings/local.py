"""The settings file used when working on the project locally.
"""

import os
import tempfile
from purse.settings.base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

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
