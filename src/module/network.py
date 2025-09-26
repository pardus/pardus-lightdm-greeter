import asyncio
from wifi import widget as wifi_widget


def _network_button_event(widget=None):
    global network_label_text
    network_label_text = _("Loading...")
    loginwindow.o("ui_popover_network").popup()
    network_control_event()


def _wifi_button_event(widget=None):
    loginwindow.o("ui_popover_wifi").popup()
    if wmenu:
        wmenu.refresh()
        wmenu.stack.set_visible_child_name("main")

def is_cable_available():
    for dev in os.listdir("/sys/class/net/"):
        if dev == "lo":
            continue
        with open("/sys/class/net/{}/operstate".format(dev),"r") as f:
            if "up" in f.read():
                return True
    return False

def is_net_available():
    ip_list = get_local_ip()
    return len(ip_list) > 0


def update_network_icon():
    if not is_cable_available():
        GLib.idle_add(loginwindow.o("ui_icon_network").set_from_icon_name, "network-error-symbolic", Gtk.IconSize.DND)
    elif not is_net_available():
        GLib.idle_add(loginwindow.o("ui_icon_network").set_from_icon_name, "network-offline-symbolic", Gtk.IconSize.DND)
    else:
        GLib.idle_add(loginwindow.o("ui_icon_network").set_from_icon_name, "network-transmit-receive-symbolic", Gtk.IconSize.DND)

@asynchronous
def update_network_icon_loop():
    while True:
        update_network_icon()
        # Check every second. TODO: remove this and trace changes
        time.sleep(1)


@asynchronous
def network_control_event():
    network_label_text = ""
    lan_ip = ""
    update_network_icon()
    ip_list = get_local_ip()
    if not is_cable_available():
        GLib.idle_add(loginwindow.o("ui_label_network").set_text,  _("No network connection"))
        return
    elif len(ip_list) == 0:
        GLib.idle_add(loginwindow.o("ui_label_network").set_text,  _("Network is not available"))
        return
    # Calculate line length
    i = 0
    for ip, dev in ip_list:
        j = len(ip) + len(dev) + 3
        if j > i:
            i = j

    for ip, dev in ip_list:
        j = len(ip) + len(dev) + 2
        lan_ip += "- {} {}{}\n".format(dev, " "*(i-j), ip)
    ctx = _("Local IP:\n{}").format(lan_ip)
    if get("show-wan-ip", False, "network"):
        wan_ip = get_ip()
        ctx += _("WAN IP:\n- {}").format(wan_ip)
    network_label_text = ctx.strip()
    GLib.idle_add(loginwindow.o("ui_label_network").set_text, network_label_text)


wmenu = None


def module_init():
    global wmenu
    wifi_widget.set_scale(scale)
    if not get("show-widget", True, "network"):
        loginwindow.o("ui_button_network").hide()
        return
    loginwindow.o("ui_button_network").connect(
        "clicked", _network_button_event)
    if get("network-check-loop", False, "network"):
        update_network_icon_loop()
    else:
        update_network_icon()
    if not wifi_widget.wifi.available():
        loginwindow.o("ui_button_wifi").hide()
    else:
        loginwindow.o("ui_button_wifi").connect(
            "clicked", _wifi_button_event)
        wmenu = wifi_widget.wifimenu()
        loginwindow.o("ui_popover_wifi").add(wmenu)
        height = int(monitor.get_common_resolution().split("x")[1])
        loginwindow.o("ui_popover_wifi").set_size_request(400*scale, height/2)
