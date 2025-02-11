from util import asynchronous
from wifi import wifi
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GObject, Gio, Gdk

try:
    import locale
    from locale import gettext as _

    # Translation Constants:
    APPNAME = "pardus-lightdm-greeter"
    TRANSLATIONS_PATH = "/usr/share/locale"
    locale.bindtextdomain(APPNAME, TRANSLATIONS_PATH)
    locale.textdomain(APPNAME)
except:
    def _(msg):
        return msg

scale = 1


def set_scale(s=1):
    global scale
    scale = s


class wifimenu(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # wifi list
        self.wifi_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.refresh_signal = False
        self.wifi_item = None

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.add(self.wifi_list)
        self.wifi_list.get_style_context().add_class("button")
        self.wifi_list.get_style_context().add_class("icon")
        self.stack.add_titled(scrolledwindow, "main", "main")

        # connecting page
        connecting_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        connecting_box.pack_start(Gtk.Label(""), True, True, 0)
        spinner = Gtk.Spinner()
        spinner.start()
        connecting_box.pack_start(spinner, False, False, 0)
        connecting_box.pack_start(
            Gtk.Label(_("Connecting...")), False, False, 0)
        connecting_box.pack_start(Gtk.Label(""), True, True, 0)
        self.stack.add_titled(connecting_box, "connecting", "connecting")

        # connect box
        self.connect_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.connect_box.pack_start(status_box, False, False, 0)
        status_box.set_spacing(5)

        self.connect_box.set_spacing(5)
        self.connect_box.get_style_context().add_class("button")
        self.connect_box.get_style_context().add_class("icon")

        self.image = Gtk.Image()
        self.image.set_pixel_size(32*scale)
        status_box.pack_start(self.image, False, False, 0)

        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        status_box.pack_start(info_box, False, False, 0)
        status_box.set_spacing(13)

        self.ssid = Gtk.Label()
        self.signal = Gtk.Label()
        self.security = Gtk.Label()
        self.ssid.set_xalign(0)
        self.signal.set_xalign(0)
        self.security.set_xalign(0)
        info_box.pack_start(self.ssid, False, False, 0)
        info_box.pack_start(self.signal, False, False, 0)
        info_box.pack_start(self.security, False, False, 0)

        def password_entry_icon_press(entry, icon_pos, event):
            entry.set_visibility(True)
            entry.set_icon_from_icon_name(1, "view-conceal-symbolic")

        def password_entry_icon_release(entry, icon_pos, event):
            entry.set_visibility(False)
            entry.set_icon_from_icon_name(1, "view-reveal-symbolic")

        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)
        self.password_entry.connect("activate", self.connect_button_event)
        self.connect_box.pack_start(self.password_entry, False, False, 0)
        self.password_entry.connect("icon-press", password_entry_icon_press)
        self.password_entry.connect(
            "icon-release", password_entry_icon_release)
        self.password_entry.set_icon_from_icon_name(1, "view-reveal-symbolic")

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.set_spacing(5)
        self.connect_box.pack_start(button_box, False, False, 0)

        self.connect_button = Gtk.Button(label=_("Connect"))
        self.connect_button.connect("clicked", self.connect_button_event)
        button_box.pack_start(self.connect_button, True, True, 0)

        self.forget_button = Gtk.Button(label=_("Forget"))
        self.forget_button.connect("clicked", self.forget_button_event)
        button_box.pack_start(self.forget_button, True, True, 0)

        def entry_change_event(widget):
            self.connect_button.set_sensitive(len(widget.get_text()) >= 8)
        self.password_entry.connect("changed", entry_change_event)
        self.password_entry.set_text("")

        self.back_button = Gtk.Button(label=_("Go Back"))
        self.back_button.connect("clicked", self.back_button_event)
        self.connect_box.pack_start(Gtk.Label(""), True, True, 0)
        self.connect_box.pack_start(self.back_button, False, False, 0)

        self.stack.add_titled(self.connect_box, "connect", "connect")

        self.connect_button.get_style_context().add_class("button")
        self.forget_button.get_style_context().add_class("button")
        self.back_button.get_style_context().add_class("button")
        self.password_entry.get_style_context().add_class("entry")

        self.stack.set_visible_child_name("main")
        self.pack_start(self.stack, True, True, 0)

        if wifi.available():
            self.show_all()
            self.connect_box.show_all()
            self.stack.show_all()
            self.refresh()

    def update_connect_box(self):
        self.password_entry.set_text("")
        if not self.wifi_item:
            return

        if int(self.wifi_item.wifi_obj.signal) > 80:
            self.image.set_from_icon_name(
                "network-wireless-signal-excellent-symbolic", 0)
        elif int(self.wifi_item.wifi_obj.signal) > 60:
            self.image.set_from_icon_name(
                "network-wireless-signal-good-symbolic", 0)
        elif int(self.wifi_item.wifi_obj.signal) > 40:
            self.image.set_from_icon_name(
                "network-wireless-signal-ok-symbolic", 0)
        else:
            self.image.set_from_icon_name(
                "network-wireless-signal-weak-symbolic", 0)

        self.ssid.set_markup(
            _("<b>SSID:</b> {}").format(self.wifi_item.wifi_obj.ssid))
        self.security.set_markup(
            _("<b>Security:</b>{}").format(self.wifi_item.wifi_obj.security))
        self.signal.set_markup(
            _("<b>Signal:</b> %{}").format(self.wifi_item.wifi_obj.signal))

        if self.wifi_item.wifi_obj.connected:
            self.connect_button.set_label(_("Disconnect"))
            self.password_entry.hide()
        else:
            self.connect_button.set_label(_("Connect"))
            self.password_entry.show()

        if not self.wifi_item.wifi_obj.need_password():
            self.password_entry.hide()
            self.connect_button.set_sensitive(True)
        else:
            self.password_entry.show()
            self.connect_button.set_sensitive(False)

        if not self.wifi_item.wifi_obj.is_saved():
            self.forget_button.hide()
        else:
            self.forget_button.show()

    def back_button_event(self, widget=None):
        self.stack.set_visible_child_name("main")
        self.refresh()

    def forget_button_event(self, widget=None):
        self.stack.set_visible_child_name("main")
        self.wifi_item.wifi_obj.forget()
        self.refresh()

    @asynchronous
    def connect_button_event(self, widget=None):
        self.stack.set_visible_child_name("connecting")
        status = False
        if not self.wifi_item:
            return
        if not self.wifi_item.wifi_obj.connected:
            status = self.wifi_item.wifi_obj.connect(
                self.password_entry.get_text())
        else:
            status = self.disconnect_button_event(widget)
        if not status:
            self.wifi_item.wifi_obj.forget()
            # TODO: implement error message
        self.stack.set_visible_child_name("main")
        self.refresh()

    @asynchronous
    def disconnect_button_event(self, widget=None):
        if not self.wifi_item:
            return
        self.wifi_item.wifi_obj.disconnect()
        self.refresh()

    def refresh(self, widget=None):
        GLib.timeout_add(1000, self.refresh_event)

    def refresh_event(self, widget=None, *args):
        if self.refresh_signal:
            print("Wifi refresh signal already pending", file=sys.stderr)
            return
        self.refresh_signal = True
        for child in self.wifi_list.get_children():
            self.wifi_list.remove(child)
            child = None

        for item in wifi.list_wifi():
            w = wifi_item(item, self)
            self.wifi_list.pack_start(w, False, False, 0)
            if "802.1X" in item.security and not item.is_saved():
                w.set_sensitive(False)
            w.show()
        self.refresh_signal = False


class wifi_item(Gtk.Box):
    def __init__(self, wifi_obj, widget_ctx=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        # wifi icon
        self.image = Gtk.Image()
        self.image.set_pixel_size(32*scale)
        self.wifi_obj = wifi_obj
        self.widget_ctx = widget_ctx
        if int(self.wifi_obj.signal) > 80:
            self.image.set_from_icon_name(
                "network-wireless-signal-excellent-symbolic", 0)
        elif int(self.wifi_obj.signal) > 60:
            self.image.set_from_icon_name(
                "network-wireless-signal-good-symbolic", 0)
        elif int(self.wifi_obj.signal) > 40:
            self.image.set_from_icon_name(
                "network-wireless-signal-ok-symbolic", 0)
        else:
            self.image.set_from_icon_name(
                "network-wireless-signal-weak-symbolic", 0)
        self.ssid = Gtk.Label()
        self.ssid.set_markup("<b>{}</b>".format(self.wifi_obj.ssid))
        self.ssid.set_xalign(0)
        self.signal = Gtk.Label()
        self.signal.set_text("%"+str(self.wifi_obj.signal))
        self.signal.set_xalign(0)
        self.security = Gtk.Label()
        self.security.set_text(self.wifi_obj.security)
        self.security.set_xalign(0)
        self.status = Gtk.Label()
        if self.wifi_obj.connected:
            self.status.set_text(_("Connected"))
        elif self.wifi_obj.is_saved():
            self.status.set_text(_("Saved"))
        elif not self.wifi_obj.need_password():
            self.status.set_text(_("Insecured"))
        elif "802.1X" in self.wifi_obj.security:
            self.status.set_text(_("Unsupported"))

        self.layout_init()

    def first_row_click_event(self, widget=None):
        self.widget_ctx.wifi_item = self
        self.widget_ctx.update_connect_box()
        self.widget_ctx.stack.set_visible_child_name("connect")

    def layout_init(self):

        first_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        first_row.pack_start(self.image, False, False, 0)
        first_row.set_spacing(13)

        label_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        label_box.pack_start(self.ssid, False, False, 0)
        label_box.pack_start(self.security, False, False, 0)
        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        first_row.pack_start(label_box, False, False, 0)
        first_row.pack_start(Gtk.Label(), True, True, 0)
        first_row.pack_start(status_box, False, False, 0)

        self.signal.set_halign(Gtk.Align.END)
        self.status.set_halign(Gtk.Align.END)
        status_box.pack_start(self.signal, False, False, 0)
        status_box.pack_start(self.status, False, False, 0)

        first_row_button = Gtk.Button()
        first_row_button.add(first_row)
        first_row_button.set_relief(Gtk.ReliefStyle.NONE)
        self.pack_start(first_row_button, True, True, 0)
        first_row_button.connect("clicked", self.first_row_click_event)

        first_row_button.get_style_context().add_class("icon")

        self.show_all()
