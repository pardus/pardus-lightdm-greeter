import subprocess
import os


class monitor_class:

    def __init__(self):
        self.screen_event_lock = False

    # common backends
    def get_monitors(self):
        if os.path.isdir("/sys/class/drm"):
            return self.get_drm_monitors()
        else:
            return self.get_xrandr_monitors()

    def get_resolutions(self, monitor):
        if os.path.isdir("/sys/class/drm"):
            return self.get_drm_resolutions(monitor)
        else:
            return self.get_xrandr_resolutions(monitor)

    #### /sys/class/drm backend ####

    def get_drm_monitors(self):
        monitors = []
        if not os.path.isdir("/sys/class/drm"):
            return monitors
        for device in os.listdir("/sys/class/drm"):
            if device.startswith("card") and os.path.isfile("/sys/class/drm/{}/modes".format(device)):
                with open("/sys/class/drm/{}/status".format(device)) as f:
                    if f.read().strip() == "connected":
                        card = device.split("-")[0]
                        monitors.append(device[len(card)+1:])
        monitors.sort()
        return monitors

    def get_device(self, monitor):
        for device in os.listdir("/sys/class/drm"):
            if device.endswith(monitor):
                return device
        return ""

    def get_drm_resolutions(self, monitor):
        ret = []
        with open("/sys/class/drm/{}/modes".format(self.get_device(monitor)), "r") as f:
            for line in f.read().split("\n"):
                if len(line) > 0 and line[0].isnumeric():
                    ret.append(line)
        if len(ret) > 0:
            return ret
        return ["800x600"]

    #### xrandr backend ####

    def get_xrandr_monitors(self):
        monitors = []
        for line in subprocess.getoutput("xrandr --listmonitors").split("\n"):
            line = line.strip()
            if not line[0].isnumeric():
                continue
            line = line.split()[1]
            for i in ["+", "*"]:
                line = line.replace(i, "")
            monitors.append(line)
        monitors.sort()
        return monitors

    def get_xrandr_resolutions(self, monitor):
        e = False
        ret = []
        for line in subprocess.getoutput("xrandr").split("\n"):
            if not line.startswith(" "):
                e = False
            if line.startswith(monitor):
                e = True
            if e and line.startswith(" "):
                ret.append(line.strip().split(" ")[0])
        if len(ret) > 0:
            return ret
        return ["800x600"]

    #### resolution finder ####

    def get_common_resolution(self):
        monitors = self.get_monitors()
        if len(monitors) < 1 or is_virtualbox():
            display = Gdk.Display.get_default()
            geom = display.get_monitor(0).get_geometry()
            return "{}x{}".format(geom.width, geom.height)
        prim_res = self.get_resolutions(monitors[0])
        for monitor in monitors[1:]:
            for res in self.get_resolutions(monitor):
                if res in prim_res:
                    return res
        return prim_res[0]

    #### functions ####

    def mirror(self):
        if self.screen_event_lock:
            return
        monitors = self.get_xrandr_monitors()
        if len(monitors) < 1:
            return
        if len(monitors) < 2:
            self.init_monitor()
        self.screen_event_lock = True

        common_resolution = self.get_common_resolution()
        for monitor in monitors:
            os.system("xrandr --output {} --pos 0x0".format(monitor))
        for monitor in monitors:
            os.system(
                "xrandr --output {} --mode {}".format(monitor, common_resolution))
        self.screen_event_lock = False
        w = int(common_resolution.split("x")[0])
        h = int(common_resolution.split("x")[1])
        update_window_resolution(w, h)

    def init_monitor(self):
        if self.screen_event_lock:
            return
        monitors = self.get_xrandr_monitors()
        if len(monitors) < 1:
            return
        wtot = 0
        self.screen_event_lock = True
        for monitor in monitors:
            resolution = self.get_xrandr_resolutions(monitor)[0]
            os.system(
                "xrandr --output {} --mode {}".format(monitor, resolution))
            os.system("xrandr --output {} --pos {}x0".format(monitor, wtot))
            wtot += int(resolution.split("x")[0])
        self.screen_event_lock = False


monitor = None


def get_monitor_offset(screen_index):
    offset = 0
    j = 0
    for m in monitor.get_monitors():
        if j == screen_index:
            return offset
        offset += int(monitor.get_resolutions(m)[0].split("x")[0])
        j += 1
    return offset


def set_window_monitor(screen_index=0):
    if monitor.screen_event_lock:
        return
    monitor.screen_event_lock = True
    monitors = monitor.get_monitors()
    if len(monitors) <= screen_index:
        screen_index = 0
    m = monitors[screen_index]
    res = monitor.get_resolutions(m)[0]
    w = int(res.split("x")[0])
    h = int(res.split("x")[1])
    new_x = get_monitor_offset(screen_index)
    loginwindow.o("ui_window_main").unfullscreen()
    loginwindow.o("ui_window_main").move(int(new_x), 0)
    loginwindow.o("ui_window_main").fullscreen()
    debug("Using primatry monitor:{}::{}::{}".format(m, res, screen_index))
    update_window_resolution(w, h)
    monitor.screen_event_lock = False


def module_init():
    global monitor
    monitor = monitor_class()
