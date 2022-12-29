import asyncio

def _network_button_event(widget=None):
    global network_label_text
    network_label_text=_("Loading...")
    loginwindow.o("ui_popover_network").popup()
    network_control_event()

network_label_text=""
_last_network_label_text=""
def update_popover_text():
    global _last_network_label_text
    if _last_network_label_text != network_label_text:
        _last_network_label_text = network_label_text
        loginwindow.o("ui_label_network").set_text(network_label_text)
    GLib.timeout_add(500,update_popover_text)

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
        network_label_text=_("Network not available")
        return
    for ip, dev in ip_list:
        j = len(ip) + len(dev) + 2
        lan_ip += "- {} {}{}\n".format(dev," "*(i-j), ip)
    ctx = _("Local IP:\n{}").format(lan_ip)
    if get("show-wan-ip",False,"network"):
        wan_ip = get_ip()
        ctx +=_("WAN IP:\n- {}").format(wan_ip)
    network_label_text=ctx.strip()


def module_init():
    if not get("show-widget",True,"network"):
        loginwindow.o("ui_button_network").hide()
    loginwindow.o("ui_button_network").connect("clicked",_network_button_event)
    update_popover_text()

