. ~/.virtualenvs/site-account/bin/activate

export DJANGO_SETTINGS_MODULE='purse.settings.local'
export PORTE_MONNAIE_SECRET_KEY='public fake key'
export PYTHONPATH='site'

echo "Use: django-admin.py runserver to run the debug server"
