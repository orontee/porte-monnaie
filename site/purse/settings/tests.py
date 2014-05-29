"""The settings file used to run unit tests.

An in-memory database is used to speedup the tests.

A simple (unsafe) password hasher is used because the default password
hasher is rather slow.

Email messages are stored in a special attribute of the
'django.core.mail' module.

"""

from purse.settings.base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

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

PASSWORD_HASHERS = (
	    'django.contrib.auth.hashers.MD5PasswordHasher',)

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
