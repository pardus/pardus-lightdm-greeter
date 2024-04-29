#!/bin/bash
set -o pipefail
python3 /usr/share/pardus/pardus-lightdm-greeter/main.py  |& tee ~/pardus-lightdm-greeter.log
if [ $? -ne 0  ] ; then
    python3 <<EOF
import gi, os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
w = Gtk.Window()
txt=open(os.environ["HOME"]+"/pardus-lightdm-greeter.log", "r").read()
l=Gtk.Label(txt)
w.add(l)
w.show_all()
Gtk.main()
EOF
fi
