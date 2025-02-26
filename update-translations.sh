#!/bin/bash

langs=$(cat po/LINGUAS)

if ! command -v xgettext &> /dev/null
then
	echo "xgettext could not be found."
	echo "you can install the package with 'apt install gettext' command on debian."
	exit
fi


echo "updating pot file"
xgettext -o po/pardus-lightdm-greeter.pot \
    --from-code="utf-8" \
    data/main.ui \
    `find src -type f -iname "*.py"`

for lang in ${langs[@]}; do
	if [[ -f po/$lang.po ]]; then
		echo "updating $lang.po"
		msgmerge -o po/$lang.po po/$lang.po po/pardus-lightdm-greeter.pot
	else
		echo "creating $lang.po"
		cp po/pardus-lightdm-greeter.pot po/$lang.po
	fi
done

