==============
 Contributing
==============

Setting up a development environment
------------------------------------

1. Fork and clone the Git repository.

2. Create and checkout a new branch.
 
3. Install the virtual environment::

     $ source share/setup_debug_env

4. Create the database::

     $ make createdb

5. Create the tables::

     $ make syncdb
