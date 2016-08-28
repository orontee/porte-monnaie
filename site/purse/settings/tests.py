"""The settings file used to run unit tests.

An in-memory database is used to speedup the tests.

A simple (unsafe) password hasher is used because the default password
hasher is rather slow.

Email messages are stored in a special attribute of the
'django.core.mail' module.

"""

from purse.settings.base import *

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
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
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        },
    },
]

PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
