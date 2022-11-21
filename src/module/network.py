import asyncio

def _network_button_event(widget=None):
    loginwindow.builder.get_object("ui_label_network").set_text(_("Loading..."))
    loginwindow.builder.get_object("ui_popover_network").popup()
    network_control_event()

@asynchronous
def network_control_event():
    lan_ip = ""
    # Calculate line length
    i = 0
    for ip, dev in get_local_ip():
        j = len(ip) + len(dev) + 3
        if j > i:
            i = j
    for ip, dev in get_local_ip():
        j = len(ip) + len(dev) + 2
        lan_ip += "- {} {}{}\n".format(dev," "*(i-j), ip)
    ctx = _("Local IP:\n{}").format(lan_ip)
    if get("show-wan-ip",False,"network"):
        wan_ip = get_ip()
        ctx +=_("WAN IP:\n- {}").format(wan_ip)
    loginwindow.builder.get_object("ui_label_network").set_text(ctx.strip())

def module_init():
    if not get("show-widget",True,"network"):
        loginwindow.builder.get_object("ui_button_network").hide()
    loginwindow.builder.get_object("ui_button_network").connect("clicked",_network_button_event)
