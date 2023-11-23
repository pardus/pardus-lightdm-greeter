def update_window_resolution(width, height):
    loginwindow.width = width
    loginwindow.height = height
    loginwindow.sync_resolution()


def _update_resolution_event(flag=None):
    debug("Screen configuration changed")
    if len(monitor.get_monitors()) < 2:
        resolution = monitor.get_common_resolution()
        w = int(resolution.split("x")[0])
        h = int(resolution.split("x")[1])
        update_window_resolution(w, h)
        return
    if get("mirror", True, "screen") and not is_virtual_machine():
        monitor.mirror()
    else:
        i = int(float(get("default-monitor", "0", "screen")))
        monitor.init_monitor()
        set_window_monitor(i)

def module_init():
    screen = loginwindow.o("ui_window_main").get_screen()
    _update_resolution_event()
    screen.connect("monitors_changed", _update_resolution_event)
    loginwindow.o("ui_window_main").set_keep_below(True)
