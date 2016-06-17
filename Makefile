SHELL = /bin/bash
INSTALL_PATH = /opt/dewey
FINAL_PATH = $(DESTDIR)$(INSTALL_PATH)

all: virtualenv

virtualenv:
	mkdir -p $(FINAL_PATH)
	virtualenv -p python3 $(FINAL_PATH)/.virtualenv
	. $(FINAL_PATH)/.virtualenv/bin/activate && pip install -r requirements/common.txt
	echo '[ -f /etc/default/dewey ] && . /etc/default/dewey' >> $(FINAL_PATH)/.virtualenv/bin/activate

install:
	mkdir -p $(FINAL_PATH)
	cp -R artwork bin README.md requirements $(FINAL_PATH)
	rsync --exclude=*.pyc --exclude=__pycache__ -r modules/ $(FINAL_PATH)/modules/
	mkdir -p $(DESTDIR)/etc/init 
	for file in `ls etc/init`; do cp etc/init/$$file $(DESTDIR)/etc/init; done 

clean:
	rm -rf $(DESTDIR)/opt
	rm -rf $(DESTDIR)/etc
