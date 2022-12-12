def update_window_resolution(width, height):
    loginwindow.width = width
    loginwindow.height = height
    loginwindow.sync_resolution()

def _update_resolution_event(flag=None):
    debug("Screen configuration changed")
    if get("mirror",True,"screen"):
        monitor.mirror()
        resolution = monitor.get_common_resolution()
    else:
        i = int(get("default-monitor",0,"screen")
        monitor.init_monitor()
        set_window_monitor(i)
        display = Gdk.Display.get_default()
        geom = display.get_monitor(i).get_geometry()
        resolution "{}x{}".format(geom.width, geom.height)
    try:
        w = int(resolution.split("x")[0])
        h = int(resolution.split("x")[1])
        update_window_resolution(w, h)
    except:
        pass


def module_init():
    screen = loginwindow.window.get_screen()
    _update_resolution_event()
    screen.connect("monitors_changed", _update_resolution_event)
    loginwindow.window.set_keep_below(True)
