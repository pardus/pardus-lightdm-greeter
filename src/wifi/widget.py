import gi, sys
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GObject, Gio, Gdk
from wifi import wifi
class wifimenu(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.wifi_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.refresh_signal=False
        if True or wifi.available():
            scrolledwindow = Gtk.ScrolledWindow()
            scrolledwindow.add(self.wifi_list)
            self.pack_start(scrolledwindow,True, True,0)
            self.show_all()
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
        if self.wifi_obj.connected:
            self.disconnect_button_event(widget)
            return
        if not self.wifi_obj.need_password() and not self.wifi_obj.connected:
            self.connect_button_event()
            return
        self.second_row_revealer.set_reveal_child(not self.second_row_revealer.get_child_revealed())
    
    def connect_button_event(self, widget=None):
        if not self.wifi_obj.connected:
            self.wifi_obj.connect(self.password_entry.get_text())
            self.widget_ctx.refresh()
        else:
            self.disconnect_button_event(widget)

    def disconnect_button_event(self, widget=None):
        print("aaaa")
        self.wifi_obj.disconnect()
        self.widget_ctx.refresh()
    
    def layout_init(self):
        connect_button = Gtk.Button(label="connect")
        connect_button.connect("clicked",self.connect_button_event)

        first_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        first_row.pack_start(self.image, False, False, 0)
        
        second_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

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
        
        self.password_entry = Gtk.Entry()
        self.password_entry.set_visibility(False)
        second_row.pack_start(self.password_entry, True, True, 0)
        second_row.pack_start(connect_button, False, False, 0)
        
        self.second_row_revealer = Gtk.Revealer()
        self.second_row_revealer.add(second_row)
        self.pack_start(self.second_row_revealer, True, True, 0)
        
        first_row_button.get_style_context().add_class("icon")
        connect_button.get_style_context().add_class("button")
        self.password_entry.get_style_context().add_class("entry")
        
        self.show_all()
        if self.wifi_obj.connected:
            second_row.hide()

