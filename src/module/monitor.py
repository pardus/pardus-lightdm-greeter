import subprocess
import os


class monitor_class:

    def __init__(self):
        self.screen_event_lock = False

    def get_monitors(self):
        monitors = []
        for device in os.listdir("/sys/class/drm"):
            if device.startswith("card") and os.path.isfile("/sys/class/drm/{}/modes".format(device)):
                with open("/sys/class/drm/{}/status".format(device)) as f:
                    if f.read().strip() == "connected":
                        card = device.split("-")[0]
                        monitors.append(device[len(card)+1:])
        return monitors

    def get_device(self,monitor):
        for device in os.listdir("/sys/class/drm"):
            if device.endswith(monitor):
                return device
        return ""

    def get_xrandr_monitor(self):
        monitors = []
        for line in subprocess.getoutput("xrandr --listmonitors").split("\n"):
            line = line.strip()
            if not line[0].isnumeric():
                continue
            line = line.split()[1]
            for i in ["+", "*"]:
                line = line.replace(i, "")
            monitors.append(line)
        return monitors

    def mirror(self):
        if self.screen_event_lock:
            return
        self.screen_event_lock = True
        common_resolution = self.get_common_resolution()
        for monitor in self.get_xrandr_monitor():
            os.system("xrandr --output {} --pos 0x0".format(monitor))
        for monitor in self.get_xrandr_monitor():
            os.system(
                "xrandr --output {} --mode {}".format(monitor, common_resolution))
        self.screen_event_lock = False

    def init_monitor(self):
        wtot = 0
        self.screen_event_lock = True
        common_resolution = self.get_common_resolution()
        for monitor in self.get_xrandr_monitor():
            os.system(
                "xrandr --output {} --mode {}".format(monitor, common_resolution))
            os.system("xrandr --output {} --pos {}x0".format(monitor, wtot))
            wtot += int(common_resolution.split("x")[0])
        self.screen_event_lock = False

    def get_common_resolution(self):
        prim_res = self.get_resolutions(self.get_monitors()[0])
        for monitor in self.get_monitors()[1:]:
            for res in self.get_resolutions(monitor):
                if res in prim_res:
                    return res
        return prim_res[0]

    def get_resolutions(self, monitor):
        with open("/sys/class/drm/{}/modes".format(self.get_device(monitor)),"r") as f:
            return f.read().split("\n")
        return ["800x600"]

monitor = None


def get_monitor_offset(screen_index):
    offset = 0
    j = 0
    for m in monitor.get_monitors():
        if j == screen_index:
            return offset
        offset = monitor.get_resolutions(m)[0].split("x")[0]
        j += 1
    return offset


def set_window_monitor(screen_index=0):
    if monitor.screen_event_lock:
        return
    monitor.screen_event_lock = True
    if type(screen_index) != type(0):
        screen_index = 0
    m = monitor.get_monitors()[screen_index]
    res = monitor.get_resolutions(m)[0]
    w = int(res.split("x")[0])
    h = int(res.split("x")[1])
    new_x = get_monitor_offset(screen_index)
    loginwindow.window.unfullscreen()
    loginwindow.window.move(int(new_x), 0)
    loginwindow.window.unfullscreen()
    update_window_resolution(w, h)
    monitor.screen_event_lock = False


def module_init():
    global monitor
    monitor = monitor_class()
