build: buildmo

buildmo:
	@echo "Building the mo files"
	for file in `ls po/*.po`; do \
		lang=`echo $$file | sed 's@po/@@' | sed 's/\.po//'`; \
		msgfmt -o po/$$lang.mo $$file; \
	done

pot:
	xgettext -o pardus-lightdm-greeter.pot --from-code="utf-8" src/data/main.ui `find src -type f -iname "*.py"`
	for file in `ls po/*.po`; do \
            msgmerge $$file pardus-lightdm-greeter.pot -o $$file.new ; \
	    echo POT: $$file; \
	    rm -f $$file ; \
	    mv $$file.new $$file ; \
	done

install: uninstall installmo
	mkdir -p $(DESTDIR)/usr/share/pardus/pardus-lightdm-greeter/
	mkdir -p $(DESTDIR)/usr/share/xgreeters/
	mkdir -p $(DESTDIR)/usr/bin
	mkdir -p $(DESTDIR)/usr/libexec
	mkdir -p $(DESTDIR)/etc/pardus
	mkdir -p $(DESTDIR)/usr/share/lightdm/lightdm.conf.d/
	mkdir -p $(DESTDIR)/usr/share/icons/hicolor/scalable/status/
	cp -prfv ./src/* $(DESTDIR)/usr/share/pardus/pardus-lightdm-greeter/
	chmod +x $(DESTDIR)/usr/share/pardus/pardus-lightdm-greeter/*
	ln -s ../../pardus/pardus-lightdm-greeter/data/lightdm.conf $(DESTDIR)/usr/share/lightdm/lightdm.conf.d/99-pardus.conf || true
	ln -s ../pardus/pardus-lightdm-greeter/data/greeter.desktop $(DESTDIR)/usr/share/xgreeters/pardus.desktop || true
	install pardus-lightdm-greeter.sh $(DESTDIR)/usr/libexec/pardus-lightdm-greeter || true
	ln -s ../../usr/share/pardus/pardus-lightdm-greeter/data/config.ini $(DESTDIR)/etc/pardus/greeter.conf || true
	chmod 755 -R $(DESTDIR)/usr/share/pardus/pardus-lightdm-greeter/
	cp -pf src/data/icon/*.svg $(DESTDIR)/usr/share/icons/hicolor/scalable/status/
	rm -rf $(DESTDIR)/usr/share/pardus/pardus-lightdm-greeter/data/icon

installmo:
	for file in `ls po/*.po`; do \
	    lang=`echo $$file | sed 's@po/@@' | sed 's/\.po//'`; \
	    mkdir -p $(DESTDIR)/usr/share/locale/$$lang/LC_MESSAGES/; \
	    install po/$$lang.mo $(DESTDIR)/usr/share/locale/$$lang/LC_MESSAGES/pardus-lightdm-greeter.mo ;\
	done

uninstallmo:
	for file in `ls po/*.po`; do \
	    lang=`echo $$file | sed 's@po/@@' | sed 's/\.po//'`; \
	    rm -f $(DESTDIR)/usr/share/locale/$$lang/LC_MESSAGES/pardus-lightdm-greeter.mo ;\
	done

uninstall: uninstallmo
	rm -rvf $(DESTDIR)/usr/share/pardus/pardus-lightdm-greeter/
	rm -fv $(DESTDIR)/usr/share/lightdm/lightdm.conf.d/99-pardus.conf
	rm -fv $(DESTDIR)/etc/pardus/greeter.conf
	rm -fv $(DESTDIR)/usr/libexec/pardus-lightdm-greeter
	rm -fv $(DESTDIR)/usr/share/xgreeters/pardus.desktop

clean:
	find -iname "__pycache__" | xargs rm -rfv
	find -iname "*.pyc" | xargs rm -rfv
	find -iname "*.ui~" | xargs rm -rfv
	find -iname "*.mo" | xargs rm -rfv
