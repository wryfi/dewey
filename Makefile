SHELL = /bin/bash
INSTALL_PATH=/opt/dewey

install: FINAL_PATH = $(DESTDIR)$(INSTALL_PATH)

all:

install:
	[ -f .gitmodules ] || git submodule init
	git submodule update --init
	cd lib && git fetch && git pull origin master && git lfs pull && cd ..
	mkdir -p $(FINAL_PATH) $(DESTDIR)/usr/bin $(DESTDIR)/etc/init $(DESTDIR)/etc/default
	[ -d $(FINAL_PATH)/.virtualenv ] || virtualenv -p python3 $(FINAL_PATH)/.virtualenv
	. $(FINAL_PATH)/.virtualenv/bin/activate && pip --version | grep 8.1 || pip install --upgrade pip
	. $(FINAL_PATH)/.virtualenv/bin/activate && pip install --upgrade setuptools
	. $(FINAL_PATH)/.virtualenv/bin/activate && pip install --no-index --find-links lib/python -r requirements/production.txt
	cp -R artwork bin README.md requirements $(FINAL_PATH)
	rsync --exclude=*.pyc --exclude=__pycache__ -rl modules/ $(FINAL_PATH)/modules/
	rsync -rl bin/ $(DESTDIR)/usr/bin/
	cp etc/defaults $(DESTDIR)/etc/default/dewey
	for file in `ls etc/init/*.conf`; do cp $$file $(DESTDIR)/etc/init; done
	for file in `ls lib/misc/*.tar.gz`; do tar xzf $$file -C $(DESTDIR); done
	virtualenv -p python3 --relocatable $(FINAL_PATH)/.virtualenv
	echo '[ -f /etc/default/dewey ] && . /etc/default/dewey' >> $(FINAL_PATH)/.virtualenv/bin/activate
	sed -i 's/^VIRTUAL_ENV.*$$/VIRTUAL_ENV="\/opt\/dewey\/.virtualenv"/' $(FINAL_PATH)/.virtualenv/bin/activate
