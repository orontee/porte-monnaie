projname = purse
projdir = site

publicdir = $(projdir)/$(projname)/public

apps = $(projdir)/$(projname)
apps += $(projdir)/tracker
apps += $(projdir)/users

dbname = porte-monnaie_data
dbuser = porte-monnaie
dbhost = localhost

manager = django-admin.py

lang = fr

setup: compile-messages

install: setup $(publicdir)/django.fcgi $(publicdir)/.htaccess collect syncdb

uninstall: 
	-rm -fr $(publicdir)

help:
	@echo "The main targets are:"
	@echo "  setup      Finalize the project environment"
	@echo "  install    Install the website"
	@echo "  uninstall  Uninstall the website"
	@echo "  createdb   Create the site database"
	@echo "  dropdb 	  Drop the site database"

.PHONY: createdb dropdb syncdb setup \
	compile-messages update-messages \
	collect

createdb: 
	-createuser -d $(dbuser) -h $(dbhost)
	-createdb $(dbname) -U $(dbuser) -h $(dbhost)

dropdb:
	-dropdb $(dbname) -U $(dbuser) -h $(dbhost)
	-dropuser $(dbuser) -h $(dbhost)

syncdb: 
	cd $(projdir); \
	$(manager) syncdb --noinput --pythonpath=.

update-messages:
	for app in $(apps); do \
		[ -x $$app/locale ] && ( \
			pushd $$app &> /dev/null; \
			django-admin.py makemessages -l $(lang) --pythonpath=..; \
			popd &> /dev/null \
		); \
	done

compile-messages:
	for app in $(apps); do \
		[ -x $$app/locale ] && ( \
			pushd $$app &> /dev/null; \
			django-admin.py compilemessages -l $(lang) --pythonpath=..; \
			popd &> /dev/null \
		); \
	done

collect: $(publicdir)/static
	cd $(projdir); \
	$(manager) collectstatic --noinput --pythonpath=.

$(publicdir):
	[ -x $@ ] || mkdir $@
	touch	$@

$(publicdir)/django.fcgi: share/django.fcgi $(publicdir)
	cp $< $(publicdir)/
	chmod +x $@

$(publicdir)/%: share/% $(publicdir)
	cp $< $(publicdir)/
