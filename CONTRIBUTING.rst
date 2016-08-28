==============
 Contributing
==============

Setting up a development environment
------------------------------------

1. Fork and clone the Git repository.

2. Create and checkout a new branch.

3. Create a virtual environment::

     purse_project$ virtualenv2 ~/.virtualenvs/purse
 
4. Adapt the script ``share/setup_debug_env`` to your setup. Then to
   enter the virtual environment, just enter the following command::

     purse_project$ source share/setup_debug_env
     ...

5. Install the dependencies listed in the file ``requirements_dev.txt``::

     (purse) purse_project$ pip install -r requirements_dev.txt
     ...

6. Create a new role called ``porte-monnaie`` for your local
   PostgreSQL service and give it access to a database called
   ``porte-monnaie_data``::

     (purse) purse_project$ make createdb

7. Finalize the project environment::

     (purse) purse_project$ make setup

Testing
-------

Just run the following commands from the source directory::

     (purse) purse_project$ make check
     Creating test database for alias 'default'...
     .............................................
     ----------------------------------------------------------------------
     Ran 45 tests in 1.519s
     
     OK
     Destroying test database for alias 'default'...

Translations
------------

When working on translations, one may use the Makefile targets
``update-messages`` to update the PO files and ``compile-messages`` to
compile those files.

