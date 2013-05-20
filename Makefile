# TODO Be consistent; Choose between django-admin.py and manage.py
# TODO Check that django-manage.py is in path when necessary

projname = porte-monnaie
projdir = site

apps = $(projdir)/$(projname)
apps += $(projdir)/tracker

dbname = $(projname)_data
dbuser = $(projname)
dbhost = postgresql1.alwaysdata.com

manager = python manage.py

lang = fr

public_files = public/django.fcgi public/.htaccess

# User targets

setup: createusers compile-messages

install: setup $(public_files) collect

uninstall: dropdb dropuser
	-rm -fr $(projname)/public

help:
	@echo "The main targets are:"
	@echo "  setup      To finalize the project environment"
	@echo "  install    To install the website"
	@echo "  uninstall  To uninstall the website"

# Internal targets

.PHONY: createdb dropdb syncdb setup \
	compile-messages update-messages \
	collect

createdb: 
	-createuser -d $(dbuser) -h $(dbhost)
	-createdb $(dbname) -U $(dbuser) -h $(dbhost)

dropdb:
	-dropdb $(dbname) -U $(dbuser) -h $(dbhost)
	-dropuser $(dbuser) -h $(dbhost)

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
		[ -x $$app/locale ] && ( \
			pushd $$app &> /dev/null; \
			django-admin.py makemessages -l $(lang); \
			popd &> /dev/null \
		); \
	done

compile-messages:
	for app in $(apps); do \
		[ -x $$app/locale ] && ( \
			pushd $$app &> /dev/null; \
			django-admin.py compilemessages -l $(lang); \
			popd &> /dev/null \
		); \
	done

collect:
	cd $(projdir); \
	$(manager) collectstatic --noinput

$(projdir)/public:
	[ -x $@ ] || mkdir $@
	touch	$@

$(projdir)/public/%: share/% $(projdir)/public
	cp $< $(projdir)/public/
