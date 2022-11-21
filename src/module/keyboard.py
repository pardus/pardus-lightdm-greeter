evdev_available=True
try:
    import evdev
    if evdev:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
except:
    evdev_available=False


class xkbButton(Gtk.Button):
    def __init__(self, layout, variant=""):
        super().__init__()
        self.layout = layout
        self.variant = variant
        if self.variant != "":
            variant = " ("+self.variant+")"
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.label = Gtk.Label()
        self.image = Gtk.Image()
        self.label.set_text("  "+layout + variant)
        self.label.set_justify(Gtk.Justification.LEFT)
        box = Gtk.Box()
        box.pack_start(self.label, False, False, 0)
        box.pack_start(Gtk.Label(), True, True, 0)
        box.pack_start(self.image, False, False, 0)
        self.add(box)
        self.show_all()

    def set_default(self, status=False):
        if status:
            self.image.set_from_icon_name("emblem-default-symbolic", 0)
        else:
            self.image.set_from_icon_name("", 0)


def is_capslock_on():
    if not evdev_available:
        return False
    for dev in devices:
        for led in dev.leds(verbose=True):
            if "LED_CAPSL" in led:
                return True
    return False


def is_numlock_on():
    if not evdev_available:
        return False
    for dev in devices:
        for led in dev.leds(verbose=True):
            if "LED_NUML" in led:
                return True
    return False


def set_keyboard(layout, variant):
    return len(subprocess.getoutput("setxkbmap {} {}".format(layout, variant))) == 0


def _keyboard_button_event(widget):
    revealer = loginwindow.builder.get_object("ui_revealer_keyboard_layout")
    status = revealer.get_reveal_child()
    revealer.set_reveal_child(not status)


def update_numlock_capslock():
    if not evdev_available:
        return 
    numlock = loginwindow.builder.get_object("ui_icon_numlock")
    capslock = loginwindow.builder.get_object("ui_icon_capslock")
    numlock.set_from_icon_name("num-off-symbolic", 0)
    capslock.set_from_icon_name("caps-off-symbolic", 0)
    if is_numlock_on():
        numlock.set_from_icon_name("num-on-symbolic", 0)
    if is_capslock_on():
        capslock.set_from_icon_name("caps-on-symbolic", 0)


def _key_press_event(widget, event):
    if event.keyval == Gdk.KEY_Num_Lock or event.keyval == Gdk.KEY_Caps_Lock:
        i = 0
        while i < 10:
            i+=1
            GLib.timeout_add(100*i, update_numlock_capslock)


def _screen_keyboard_event(widget):
    os.system(get("screen-keyboard", "onboard", "keyboard")+"&")

_keyboardlist_loaded = False
def load_keyboardlist():
    global _keyboardlist_loaded
    if _keyboardlist_loaded:
        return
    _keyboardlist_loaded = True
    xkbs = get("keyboard-layouts", "tr tr:f us", "keyboard")
    xkb_buttons = {}
    loginwindow.builder.get_object("ui_button_keyboard_layout").connect(
        "clicked", _keyboard_button_event)
    loginwindow.builder.get_object("ui_button_virtual_keyboard").connect(
        "clicked", _screen_keyboard_event)
    box = loginwindow.builder.get_object("ui_box_keyboard_layout")
    for xkb in xkbs.split(" "):
        try:
            layout = xkb.split(":")[0]
            variant = xkb.split(":")[1]
            label = xkb.split(":")[2]
        except:
            continue
        def button_event(widget):
            set_keyboard(widget.layout, widget.variant)
            for x in xkb_buttons:
                xkb_buttons[x].set_default()
                widget.set_default(True)
        xkb_buttons[layout+":"+variant] = xkbButton(layout, variant)
        if len(label.strip())>0:
            xkb_buttons[layout+":"+variant].label.set_text(label.replace("_"," "))
        box.add(xkb_buttons[layout+":"+variant])
        xkb_buttons[layout+":"+variant].connect("clicked", button_event)
    try:
        layout = subprocess.getoutput(
            "setxkbmap -query | grep layout").split()[-1]
        variant = subprocess.getoutput(
            "setxkbmap -query | grep variant").split()[-1]
    except:
        layout = "tr"
        variant = ""
    debug(layout+":"+variant)
    if (layout+":"+variant) in xkb_buttons:
        xkb_buttons[layout+":"+variant].set_default(True)


def module_init():
    if get("numlock-on",True,"keyboard"):
        os.system("numlockx on")
    if evdev_available:
        loginwindow.window.connect("key-press-event", _key_press_event)
        update_numlock_capslock()
    elif not evdev_available:
        loginwindow.builder.get_object("ui_box_numlock_capslock").hide()
    load_keyboardlist()
