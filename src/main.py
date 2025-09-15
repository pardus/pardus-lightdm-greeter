#!/usr/bin/python3
import os
import sys
import time
import subprocess
from util import *

import traceback

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

ctime = time.time()
appdir = os.path.dirname(os.path.abspath(__file__))
os.chdir(appdir)
os.umask(0o077)
try:
    import locale
    from locale import gettext as _

    # Translation Constants:
    APPNAME = "pardus-lightdm-greeter"
    TRANSLATIONS_PATH = "/usr/share/locale"
    locale.bindtextdomain(APPNAME, TRANSLATIONS_PATH)
    locale.textdomain(APPNAME)
except:
    # locale load issue fix
    def _(msg):
        return msg


os.environ["UBUNTU_MENUPROXY"] = ""
os.environ["SESSION_MANAGER"] = "lightdm"
if get("touch-mode", False):
    os.environ["GTK_TEST_TOUCHSCREEN"] = "1"
os.environ["GDK_CORE_DEVICE_EVENTS"] = "1"
os.system("xhost +local: 2>/dev/null")
os.system("xset s {0} {0}".format(get("blank-timeout", 300)))

os.system(get("init", ""))

# Theme settings
settings = Gtk.Settings.get_default()
gtk_theme = get("gtk-theme", "Adwaita")
icon_theme = get("gtk-icon-theme-name", "Adwaita")
settings.set_property("gtk-application-prefer-dark-theme",
                      get("dark-theme", True))
if os.path.exists("/usr/share/themes/{}".format(gtk_theme)):
    settings.set_property("gtk-theme-name", gtk_theme)
else:
    settings.set_property("gtk-theme-name", "Adwaita")
if os.path.exists("/usr/share/themes/{}".format(icon_theme)):
    settings.set_property("gtk-icon-theme-name", icon_theme)
else:
    settings.set_property("gtk-icon-theme-name", "Adwaita")

scale = 1


def set_scale(new_scale=0):
    global scale
    scale = new_scale
    if scale < 1:
        scale = 1
    os.environ["GDK_SCALE"] = str(int(scale))
    # os.environ["GDK_DPI_SCALE"] = str(1/scale)
    settings.set_property(
        "gtk-font-name", "{} {}".format(get("font", "Regular"), int(10*(scale % 1 + 1))))
    settings.set_property("gtk-xft-dpi", 1024*96*scale)
    settings.set_property("gtk-xft-antialias", True)


set_scale(float(get("scale", "0")))

loaded_modules = []
base_modules = ["lightdm.py", "gtkwindow.py", "monitor.py"]
for module in base_modules + os.listdir("module"):
    if module in loaded_modules:
        continue
    if not os.path.isfile("module/{}".format(module)) or not module.endswith(".py"):
        continue
    with open("module/{}".format(module), "r") as f:
        debug("Loading:{}".format(module))
        try:
            exec(f.read())
            if get("load-async", False):
                if module in base_modules:
                    module_init()
                else:
                    GLib.idle_add(module_init)
            else:
                module_init()
            del (module_init)
        except Exception as e:
            print(module, traceback.format_exc(), file=sys.stderr)
        loaded_modules.append(module)
loginwindow.greeter_loaded = True
ltime = time.time()
os.chdir(os.environ["HOME"])
debug("Loading finished: {}".format(ltime-ctime))
loginwindow.o("ui_window_main").show()
loginwindow.o("ui_window_main").present()

Gtk.main()
