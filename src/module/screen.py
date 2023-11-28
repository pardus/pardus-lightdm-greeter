def update_window_resolution(width, height):
    loginwindow.width = width
    loginwindow.height = height
    loginwindow.sync_resolution()


def _update_resolution_event(flag=None):
    debug("Screen configuration changed")
    resolution = None
    if get("mirror", True, "screen") and not is_virtual_machine():
        monitor.mirror()
        resolution = monitor.get_common_resolution()
    else:
        i = int(float(get("default-monitor", "1", "screen")))
        monitor.init_monitor()
        mlist = monitor.get_monitors()
        if len(mlist) -1 < i:
            i = len(mlist)-1
        m = mlist[i]
        resolution = monitor.get_resolutions(m)[0]
        set_window_monitor(i)
    try:
        w = int(resolution.split("x")[0])
        h = int(resolution.split("x")[1])
        update_window_resolution(w, h)
    except:
        pass


def module_init():
    screen = loginwindow.o("ui_window_main").get_screen()
    _update_resolution_event()
    screen.connect("monitors_changed", _update_resolution_event)
    loginwindow.o("ui_window_main").set_keep_below(True)
