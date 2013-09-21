===============
 Porte-monnaie
===============

A web application for people to track and share their expenditures.

Installation
------------

1. Make sure that the host satisfies the dependancies listed in the
   file `requirements.txt`.

2. Some Django settings are inherited from the environment: You must
   set the following environment variables `DJANGO_SETTINGS_MODULE`,
   `DJANGO_SECRET_KEY`, `DJANGO_ADMIN_NAME`, `DJANGO_ADMIN_EMAIL`,
   `DJANGO_DATABASE`, `EMAIL_HOST`, `EMAIL_HOST_USER` and
   `EMAIL_HOST_PASSWORD`.

   For example, add to the file `.bash_profile` the following line::

     export DJANGO_SETTINGS_MODULE='purse.settings.production'

   If your site is using Fast CGI, you'll also have to set those
   variables in the file `share/django.fcgi`.

3. Create the database::

     $ make createdb

4. Install application::

     $ make install

That's all!
