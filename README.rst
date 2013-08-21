===============
 Porte-monnaie
===============

A web application for people to track and share their expenditures.

Installation
------------

1. Make sure that the host satisfies the dependancies listed in the
   file `requirements.txt`.

2. Set the environment variable `DJANGO_SETTINGS_MODULE`; For example,
   add to the file `.bash_profile` the following line::

     export DJANGO_SETTINGS_MODULE='purse.settings.production'

   The Django variable `SECRET_KEY` is automatically inherited from
   the environment variable `PORTE_MONNAIE_SECRET_KEY`. Thus you also
   have to set that variable.

3. Create the database::

     $ make createdb

4. Install application::

     $ make install

5. Create some users::

     $ cd site
     site$ django-admin.py createuser USERNAME EMAIL PASSWORD --pythonpath=.

That's all!
