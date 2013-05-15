projname = porte-monnaie
projdir = site

apps = $(projdir)/$(projname)
apps += $(projdir)/tracker

dbname = $(projname)

manager = python manage.py
# TODO Be consistent; Choose between django-admin.py and manage.py

lang = fr

PHONY: collect createdb compile-messages setup syncdb update-messages

setup: createusers

createdb:
	-createdb $(dbname)

syncdb: createdb
	cd $(projdir); \
	$(manager) syncdb --no-input

createusers: syncdb
	# cd $(projdir); \
	# $(manager) createsuperuser --username=$(superuser) --email=$(superuser_mail)

install: collect

collect:
	cd $(projdir); \
	$(manager) collectstatic --noinput

# TODO Configure STATIC_ROOT before running that target

# removedb:

# distclean:

# clean:

# uninstall:

# help:

update-messages:
	for app in $(apps); do \
		pushd $$app &> /dev/null; \
		django-admin.py makemessages -l $(lang); \
		popd &> /dev/null; \
	done

compile-messages:
	for app in $(apps); do \
		pushd $$app &> /dev/null; \
		django-admin.py compilemessages -l $(lang); \
		popd &> /dev/null; \
	done
