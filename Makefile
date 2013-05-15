projname = porte-monnaie
projdir = site

apps = $(projdir)/$(projname)
apps += $(projdir)/tracker

dbname = $(projname)

manager = python manage.py
# TODO Be consistent; Choose between django-admin.py and manage.py

lang = fr

.PHONY: collect createdb compile-messages setup syncdb update-messages

# User targets

setup: createusers compile-messages

install: setup collect

uninstall: dropdb

help:
	@echo "The main targets are:"
	@echo "  setup      To finalize the project environment"
	@echo "  install    To install the website"
	@echo "  uninstall  To uninstall the website"

# Internal targets

createdb:
	-createdb $(dbname)

dropdb:
	-dropdb $(dbname)

syncdb: createdb
	cd $(projdir); \
	$(manager) syncdb --noinput

createusers: syncdb
	cd $(projdir); \
	$(manager) createuser matthias orontee@gmail.com matthias \
				  --first=Matthias --last=Meulien; \
	$(manager) createuser laurence laurence.turridano@gmail.com laurence \
				  --first=Laurence --last=Turridano;

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

collect:
	cd $(projdir); \
	$(manager) collectstatic --noinput

# TODO Configure STATIC_ROOT before running that target

