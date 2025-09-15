_lang = ""
if "LANG" in os.environ:
    _lang = "["+str(os.environ["LANG"].split("_")[0])+"]"


class sessionButton(Gtk.Button):
    def __init__(self, session):
        super().__init__()
        self.set_can_focus(False)
        self.get_style_context().add_class("icon")
        self.session = session
        self.session_name = self.get_session_name()
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.label = Gtk.Label()
        self.image = Gtk.Image()
        self.image.set_pixel_size(12*scale)
        self.label.set_text(self.session_name)
        box = Gtk.Box()
        box.pack_start(self.label, False, False, 0)
        box.pack_start(Gtk.Label(), True, True, 0)
        box.pack_start(self.image, False, False, 0)
        box.set_margin_start(13*scale)
        box.show_all()
        self.add(box)

    def set_default(self, status=False):
        if status:
            self.image.set_from_icon_name("emblem-default-symbolic", 0)
            gsettings_set("last-session", self.session)
        else:
            self.image.set_from_icon_name("", 0)

    def get_session_name(self):
        session = ""
        for path in ["/usr/share/xsessions/{}.desktop".format(self.session),
                     "/usr/share/wayland-sessions/{}.desktop".format(self.session)]:
            if os.path.exists(path):
                for line in open(path, "r").read().split("\n"):
                    for n in ["Name"+_lang+"=", "Name="]:
                        if n in line:
                            session = line.replace(n, "")
                            break
        if session == "":
            session = self.session
        return session


_sessionlist_loaded = False


def load_sessionlist():
    global _sessionlist_loaded
    if _sessionlist_loaded:
        return
    _sessionlist_loaded = True
    box = loginwindow.o("ui_box_session")
    sessions = lightdm.get_session_list()
    for session in sessions:
        session_buttons[session] = sessionButton(session)

        def button_event(widget):
            lightdm.set(session=widget.session)
            for b in session_buttons:
                session_buttons[b].set_default(False)
            widget.set_default(True)
        session_buttons[session].connect("clicked", button_event)
        box.add(session_buttons[session])
        box.show_all()
    last_session = gsettings_get("last-session")
    if last_session == "" or last_session not in sessions:
        last_session = sessions[0]
    lightdm.set(session=last_session)
    session_buttons[last_session].set_default(True)


def _session_button_event(widget):
    revealer = loginwindow.o("ui_revealer_default_session")
    status = revealer.get_reveal_child()
    revealer.set_reveal_child(not status)
    if status:
        loginwindow.o("ui_icon_default_session_dd").set_from_icon_name(
            "go-next-symbolic", 0)
    else:
        loginwindow.o("ui_icon_default_session_dd").set_from_icon_name(
            "go-down-symbolic", 0)


session_buttons = {}


def module_init():
    global session_buttons
    loginwindow.o("ui_button_default_session").connect(
        "clicked", _session_button_event)
    load_sessionlist()
