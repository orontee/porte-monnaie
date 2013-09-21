#!/usr/bin/python
import os, sys

_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_DIR)
sys.path.insert(0, os.path.dirname(_PROJECT_DIR))

_PROJECT_NAME = _PROJECT_DIR.split('/')[-1]
os.environ['DJANGO_SETTINGS_MODULE'] = "%s.settings" % _PROJECT_NAME

# REMARK The following environment variables must be set

# os.environ['DJANGO_SECRET_KEY'] = ''
# os.environ['DJANGO_ADMIN_NAME'] = ''
# os.environ['DJANGO_ADMIN_EMAIL'] = ''
# os.environ['DJANGO_DATABASE_HOST'] = ''

# os.environ['EMAIL_HOST'] = ''
# os.environ['EMAIL_HOST_USER'] = ''
# os.environ['EMAIL_HOST_PASSWORD'] = ''


from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
