==============
 Contributing
==============

Setting up a development environment
------------------------------------

1. Fork and clone the Git repository.

2. Create and checkout a new branch.

3. Create a virtual environment satisfying the dependancies listed in
   the file `requirements.txt`.
 
4. Adapt the script `share/setup_debug_env` to your setup then enter
   the virtual environment::

     $ source share/setup_debug_env

   To run the debug server, use::

     $ django-admin.py runserver

Translations
------------

When working on translations, one may use the Makefile targets
`update-messages` to update the PO files and `compile-messages` to
compile those files.

