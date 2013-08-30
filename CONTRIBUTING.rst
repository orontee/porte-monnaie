==============
 Contributing
==============

Setting up a development environment
------------------------------------

1. Fork and clone the Git repository.

2. Create and checkout a new branch.

3. Create a virtual environment satisfying the dependancies listed in
   the file `requirements.txt`::

     purse_project$ virtualenv2 ~/.virtualenvs/purse
     purse_project$ source ~/.virtualenvs/purse/bin/activate
     (purse) purse_project$ pip install -r requirements.txt
     ...
 
4. Adapt the script `share/setup_debug_env` to your setup. Then to
   enter the virtual environment, just enter the following command::

     purse_project$ source share/setup_debug_env
     ...


Translations
------------

When working on translations, one may use the Makefile targets
`update-messages` to update the PO files and `compile-messages` to
compile those files.

