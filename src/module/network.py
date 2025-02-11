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


network_label_text = ""
_last_network_label_text = ""


def update_popover_text():
    global _last_network_label_text
    if _last_network_label_text != network_label_text:
        _last_network_label_text = network_label_text
        loginwindow.o("ui_label_network").set_text(network_label_text)
    GLib.timeout_add(500, update_popover_text)


@asynchronous
def network_control_event():
    global network_label_text
    lan_ip = ""
    # Calculate line length
    i = 0
    for ip, dev in get_local_ip():
        j = len(ip) + len(dev) + 3
        if j > i:
            i = j
    ip_list = get_local_ip()
    if len(ip_list) == 0:
        network_label_text = _("Network is not available")
        return
    for ip, dev in ip_list:
        j = len(ip) + len(dev) + 2
        lan_ip += "- {} {}{}\n".format(dev, " "*(i-j), ip)
    ctx = _("Local IP:\n{}").format(lan_ip)
    if get("show-wan-ip", False, "network"):
        wan_ip = get_ip()
        ctx += _("WAN IP:\n- {}").format(wan_ip)
    network_label_text = ctx.strip()


wmenu = None


def module_init():
    global wmenu
    wifi_widget.set_scale(scale)
    if not get("show-widget", True, "network"):
        loginwindow.o("ui_button_network").hide()
        return
    loginwindow.o("ui_button_network").connect(
        "clicked", _network_button_event)
    update_popover_text()
    if not wifi_widget.wifi.available():
        loginwindow.o("ui_button_wifi").hide()
    else:
        loginwindow.o("ui_button_wifi").connect(
            "clicked", _wifi_button_event)
        wmenu = wifi_widget.wifimenu()
        loginwindow.o("ui_popover_wifi").add(wmenu)
        height = int(monitor.get_common_resolution().split("x")[1])
        loginwindow.o("ui_popover_wifi").set_size_request(400*scale, height/2)
