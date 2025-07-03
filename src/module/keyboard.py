xlib_available = True
try:
    import Xlib
    from Xlib import display
    DISPLAY = Xlib.display.Display()
except:
    xlib_available = False


class xkbButton(Gtk.Button):
    def __init__(self, layout, variant=""):
        super().__init__()
        self.set_can_focus(False)
        self.get_style_context().add_class("icon")
        self.layout = layout
        self.variant = variant
        if self.variant != "":
            variant = " ("+self.variant+")"
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.label = Gtk.Label()
        self.image = Gtk.Image()
        self.image.set_pixel_size(12*scale)
        self.label.set_label(layout + variant)
        self.label.set_justify(Gtk.Justification.LEFT)
        box = Gtk.Box()
        box.pack_start(self.label, False, False, 0)
        box.pack_start(Gtk.Label(), True, True, 0)
        box.pack_start(self.image, False, False, 0)
        box.set_margin_start(13*scale)
        self.add(box)
        self.show_all()

    def set_default(self, status=False):
        if status:
            self.image.set_from_icon_name("emblem-default-symbolic", 0)
            os.system("setxkbmap {} {}".format(self.layout, self.variant))
        else:
            self.image.set_from_icon_name("", 0)


def is_capslock_on():
    c = DISPLAY.get_keyboard_control()
    return c.led_mask & 1


def is_numlock_on():
    c = DISPLAY.get_keyboard_control()
    return c.led_mask & 2


def _keyboard_button_event(widget):
    revealer = loginwindow.o("ui_revealer_keyboard_layout")
    status = revealer.get_reveal_child()
    if status:
        loginwindow.o("ui_icon_keyboard_layout_dd").set_from_icon_name(
            "go-next-symbolic", 0)
    else:
        loginwindow.o("ui_icon_keyboard_layout_dd").set_from_icon_name(
            "go-down-symbolic", 0)
    revealer.set_reveal_child(not status)


def update_numlock_capslock():
    if not xlib_available:
        return
    numlock = loginwindow.o("ui_icon_numlock")
    capslock = loginwindow.o("ui_icon_capslock")
    numlock.set_from_icon_name("numlock-off-symbolic", 0)
    capslock.set_from_icon_name("capslock-off-symbolic", 0)
    if is_numlock_on():
        numlock.set_from_icon_name("numlock-on-symbolic", 0)
    if is_capslock_on():
        capslock.set_from_icon_name("capslock-on-symbolic", 0)


def _key_press_event(widget, event):
    if event.keyval == Gdk.KEY_Num_Lock or event.keyval == Gdk.KEY_Caps_Lock:
        i = 0
        while i < 10:
            i += 1
            GLib.timeout_add(100*i, update_numlock_capslock)


def _screen_keyboard_event(widget):
    os.system(get("screen-keyboard", "onboard", "keyboard")+"&")


_keyboardlist_loaded = False


def load_keyboardlist():
    global _keyboardlist_loaded
    if _keyboardlist_loaded:
        return
    _keyboardlist_loaded = True
    keyboard_default = "tr::Türkçe tr:f:Türkçe_F us::İngilizce"
    xkbs = get("keyboard-layouts", keyboard_default, "keyboard")
    loginwindow.o("ui_button_keyboard_layout").connect(
        "clicked", _keyboard_button_event)
    loginwindow.o("ui_button_virtual_keyboard").connect(
        "clicked", _screen_keyboard_event)
    if len(xkbs.strip()) == 0:
        loginwindow.o("ui_button_keyboard_layout").hide()
    query = subprocess.getoutput("setxkbmap -query")
    layout = "tr"
    variant = ""
    for line in query.split("\n"):
        if "layout" in line:
            layout = line[len(line.split(":")[0])+1:].strip()
        if "variant" in line:
            variant = line[len(line.split(":")[0])+1:].strip()

    if xkbs != keyboard_default:
        xkb_buttons = _get_xkbs_buttons(xkbs)
    elif layout == "tr":
        xkb_buttons = _get_xkbs_buttons(keyboard_default)
    else:
        xkb_buttons = _get_xkbs_buttons(
            "{}:{}:{}".format(layout, variant, _("Default")))

    debug(layout+":"+variant)
    if (layout+":"+variant) in xkb_buttons:
        xkb_buttons[layout+":"+variant].set_default(True)


def _get_xkbs_buttons(xkbs):
    xkb_buttons = {}
    box = loginwindow.o("ui_box_keyboard_layout")
    for xkb in xkbs.split(" "):
        try:
            layout = xkb.split(":")[0]
            variant = xkb.split(":")[1]
            label = xkb.split(":")[2]
        except:
            continue

        def button_event(widget):
            for x in xkb_buttons:
                xkb_buttons[x].set_default()
                widget.set_default(True)
        xkb_buttons[layout+":"+variant] = xkbButton(layout, variant)
        if len(label.strip()) > 0:
            xkb_buttons[layout+":" +
                        variant].label.set_text(label.replace("_", " "))
        box.add(xkb_buttons[layout+":"+variant])
        xkb_buttons[layout+":"+variant].connect("clicked", button_event)
    return xkb_buttons


def enable_numlock():
    # Connect to the X server
    d = display.Display()
    root = d.screen().root

    # Get the current state of the keyboard
    keymap = root.get_keyboard_mapping()

    # Define the Num Lock keycode (usually 77, but can vary)
    num_lock_keycode = 77

    # Check if Num Lock is already enabled
    num_lock_state = (keymap[num_lock_keycode] & 1) != 0

    if not num_lock_state:
        # Send a key press and release event for Num Lock
        root.grab_key(num_lock_keycode, 0, X.GrabModeAsync, X.GrabModeAsync)
        root.send_event(request.KeyPress(keycode=num_lock_keycode))
        root.send_event(request.KeyRelease(keycode=num_lock_keycode))
        d.flush()


def module_init():
    if get("numlock-on", True, "keyboard"):
        os.system("numlockx on")
    if xlib_available and not is_virtualbox():
        loginwindow.o("ui_window_main").connect(
            "key-press-event", _key_press_event)
        update_numlock_capslock()
    else:
        loginwindow.o("ui_box_numlock_capslock").hide()
    load_keyboardlist()
