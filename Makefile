build: buildmo

buildmo:
	@echo "Building the mo files"
	for file in `ls po/*.po`; do \
		lang=`echo $$file | sed 's@po/@@' | sed 's/\.po//'`; \
		msgfmt -o po/$$lang.mo $$file; \
	done

pot:
	xgettext -o pardus-greeter.pot --from-code="utf-8" src/data/main.ui `find src -type f -iname "*.py"`
	for file in `ls po/*.po`; do \
            msgmerge $$file pardus-greeter.pot -o $$file.new ; \
	    echo POT: $$file; \
	    rm -f $$file ; \
	    mv $$file.new $$file ; \
	done

install: installmo
	mkdir -p $(DESTDIR)/usr/share/pardus/pardus-greeter/
	mkdir -p $(DESTDIR)/usr/share/xgreeters/
	mkdir -p $(DESTDIR)/usr/bin
	mkdir -p $(DESTDIR)/etc/pardus
	mkdir -p $(DESTDIR)/usr/share/lightdm/lightdm.conf.d/
	mkdir -p $(DESTDIR)/usr/share/icons/hicolor/scalable/status/
	mkdir -p $(DESTDIR)/sbin
	cp -prfv ./src/* $(DESTDIR)/usr/share/pardus/pardus-greeter/
	chmod +x $(DESTDIR)/usr/share/pardus/pardus-greeter/*
	install src/data/lightdm.conf $(DESTDIR)/usr/share/lightdm/lightdm.conf.d/99-pardus.conf
	install src/data/servers.txt $(DESTDIR)/usr/share/pardus/pardus-greeter/servers.txt
	ln -s ../pardus/pardus-greeter/data/greeter.desktop $(DESTDIR)/usr/share/xgreeters/pardus.desktop || true
	ln -s ../share/pardus/pardus-greeter/main.py $(DESTDIR)/usr/bin/pardus-greeter || true
	ln -s ../../usr/share/pardus/pardus-greeter/data/config.ini $(DESTDIR)/etc/pardus/greeter.conf || true
	chmod 755 -R $(DESTDIR)/usr/share/pardus/pardus-greeter/
	cp -pf src/data/icon/*.svg $(DESTDIR)/usr/share/icons/hicolor/scalable/status/

installmo:
	for file in `ls po/*.po`; do \
	    lang=`echo $$file | sed 's@po/@@' | sed 's/\.po//'`; \
	    mkdir -p $(DESTDIR)/usr/share/locale/$$lang/LC_MESSAGES/; \
	    install po/$$lang.mo $(DESTDIR)/usr/share/locale/$$lang/LC_MESSAGES/pardus-greeter.mo ;\
	done

clean:
	find -iname "__pycache__" | xargs rm -rfv
	find -iname "*.pyc" | xargs rm -rfv
	find -iname "*.ui~" | xargs rm -rfv
	find -iname "*.mo" | xargs rm -rfv
