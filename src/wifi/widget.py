import gi, sys
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GObject, Gio, Gdk
from wifi import wifi
class wifimenu(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.wifi_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.refresh_signal=False
        self.wifi_item = None

        self.stack = Gtk.Stack()

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.add(self.wifi_list)
        self.stack.add_titled(scrolledwindow,"main","main")

        self.connect_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.connect_button = Gtk.Button(label="connect")
        self.connect_button.connect("clicked",self.connect_button_event)

        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)
        self.connect_box.pack_start(self.password_entry, False, False, 0)
        self.connect_box.pack_start(self.connect_button, False, False, 0)
        self.stack.add_titled(self.connect_box,"connect","connect")


        self.connect_button.get_style_context().add_class("button")
        self.password_entry.get_style_context().add_class("entry")

        self.stack.set_visible_child_name("main")
        self.pack_start(self.stack,True,True,0)

        if True or wifi.available():
            self.show_all()
            self.connect_box.show_all()
            self.stack.show_all()
            self.refresh()

    def update_connect_box(self):
        if not self.wifi_item:
            return

        if self.wifi_item.wifi_obj.connected:
            self.connect_button.set_label("disconnect")
            self.password_entry.hide()
        else:
            self.connect_button.set_label("connect")
            self.password_entry.show()

        if not self.wifi_item.wifi_obj.need_password():
            self.password_entry.hide()


    def connect_button_event(self, widget=None):
        print(self.wifi_item,file=sys.stderr)
        if not self.wifi_item:
            return
        if not self.wifi_item.wifi_obj.connected:
            self.wifi_item.wifi_obj.connect(self.password_entry.get_text())
        else:
            self.disconnect_button_event(widget)

        self.refresh()
        self.stack.set_visible_child_name("main")


    def disconnect_button_event(self, widget=None):
        if not self.wifi_item:
            return
        self.wifi_item.wifi_obj.disconnect()
        self.refresh()


    def refresh(self,widget=None):
        GLib.timeout_add(1000,self.refresh_event)

    def refresh_event(self,widget=None, *args):
        if self.refresh_signal:
            print("Wifi refresh signal already pending",file=sys.stderr)
            return
        self.refresh_signal=True
        for child in self.wifi_list.get_children():
            self.wifi_list.remove(child)
            child = None

        for item in wifi.list_wifi():
            w = wifi_item(item, self)
            self.wifi_list.pack_start(w,False, False,0)
            w.show()
        self.refresh_signal=False



class wifi_item(Gtk.Box):
    def __init__(self,wifi_obj, widget_ctx=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        # wifi icon
        self.image = Gtk.Image()
        self.image.set_pixel_size(48)
        self.wifi_obj = wifi_obj
        self.widget_ctx = widget_ctx
        if int(self.wifi_obj.signal) > 80:
            self.image.set_from_icon_name("network-wireless-signal-excellent-symbolic",0)
        elif int(self.wifi_obj.signal) > 60:
            self.image.set_from_icon_name("network-wireless-signal-good-symbolic",0)
        elif int(self.wifi_obj.signal) > 40:
            self.image.set_from_icon_name("network-wireless-signal-ok-symbolic",0)
        else:
            self.image.set_from_icon_name("network-wireless-signal-weak-symbolic",0)
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
            self.status.set_text("connected")
        elif self.wifi_obj.is_saved():
            self.status.set_text("saved")
        elif not self.wifi_obj.need_password():
            self.status.set_text("insecured")

        self.layout_init()

    def first_row_click_event(self, widget=None):
        self.widget_ctx.wifi_item = self
        self.widget_ctx.update_connect_box()
        self.widget_ctx.stack.set_visible_child_name("connect")

    def layout_init(self):

        first_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        first_row.pack_start(self.image, False, False, 0)
        first_row.set_spacing(5)

        label_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        label_box.pack_start(self.ssid, False, False, 0)
        label_box.pack_start(self.security, False, False, 0)
        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        first_row.pack_start(label_box, False, False, 0)
        first_row.pack_start(Gtk.Label(), True, True, 0)
        first_row.pack_start(status_box, False, False, 0)

        self.signal.set_halign(Gtk.Align.END)
        self.status.set_halign(Gtk.Align.END)
        status_box.pack_start(self.signal,False,False,0)
        status_box.pack_start(self.status,False,False,0)

        first_row_button = Gtk.Button()
        first_row_button.add(first_row)
        first_row_button.set_relief(Gtk.ReliefStyle.NONE)
        self.pack_start(first_row_button, True, True, 0)
        first_row_button.connect("clicked",self.first_row_click_event)

        first_row_button.get_style_context().add_class("icon")

        self.show_all()

