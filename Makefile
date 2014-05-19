projname = purse
projdir = site

contribdir = share/contrib
publicdir = $(projdir)/$(projname)/public

apps = $(projdir)/$(projname)
apps += $(projdir)/tracker
apps += $(projdir)/users
apps += $(projdir)/bootstrap

dbname = porte-monnaie_data
dbuser = porte-monnaie
dbhost = localhost

manager = django-admin.py

lang = fr

bootstrap_archive = $(contribdir)/bootstrap-3.1.0-dist.zip
jquery_src = $(contribdir)/jquery-1.11.0.min.js
d3_archive = $(contribdir)/d3.zip

setup: compile-messages
setup: $(projdir)/bootstrap/static/js/jquery.min.js
setup: $(projdir)/bootstrap/static/bootstrap
setup: $(projdir)/tracker/static/js/d3.js $(projdir)/tracker/static/js/d3.min.js

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
		[ ! -x $$app/locale ] || ( \
			cd $$app; \
			django-admin.py makemessages -l $(lang) --pythonpath=..; \
			cd .. \
		); \
	done
	cd $(projdir)/tracker; \
	django-admin.py makemessages -l $(lang) --pythonpath=.. -d djangojs

compile-messages:
	for app in $(apps); do \
		[ ! -x $$app/locale ] || ( \
			cd $$app; \
			django-admin.py compilemessages -l $(lang) --pythonpath=..; \
			cd .. \
		); \
	done
	cd $(projdir)/tracker; \
	django-admin.py compilemessages -l $(lang) --pythonpath=..

collect:
	cd $(projdir); \
	$(manager) collectstatic --noinput --pythonpath=.

test:
	cd $(projdir); \
	$(manager) test --settings=purse.settings.tests --pythonpath=.

$(publicdir):
	[ -x $@ ] || mkdir $@

$(publicdir)/django.fcgi: share/django.fcgi | $(publicdir)
	cp $< $(publicdir)/
	chmod +x $@

$(publicdir)/%: share/% | $(publicdir)
	cp $< $(publicdir)/

$(projdir)/bootstrap/static/bootstrap: $(bootstrap_archive)
	$(manager) installbs $<

$(projdir)/bootstrap/static/js/jquery.min.js: $(jquery_src) | $(projdir)/bootstrap/static/js
	cp $< $@

$(projdir)/bootstrap/static/js:
	[ -x $@ ] || mkdir -p $@

$(projdir)/tracker/static/js/d3.js: $(d3_archive)
	unzip -o $< d3.js -d $(projdir)/tracker/static/js

$(projdir)/tracker/static/js/d3.min.js: $(d3_archive)
	unzip -o $< d3.min.js -d $(projdir)/tracker/static/js
