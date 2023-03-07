class action_button(Gtk.Button):
    def __init__(self, label, icon, command):
        super().__init__()
        self.command = command
        self.connect("clicked", self.run)
        self.label = Gtk.Label()
        self.image = Gtk.Image()
        self.image.get_style_context().add_class("icon")
        self.label.set_text("  "+label)
        self.label.get_style_context().add_class("text")
        self.image.set_from_icon_name(icon, 32)
        box = Gtk.Box()
        box.pack_start(self.image, False, False, 0)
        box.pack_start(self.label, False, False, 0)
        box.show_all()
        self.add(box)
        self.get_style_context().add_class("button")
        self.show_all()

    def run(self, widget):
        os.system("dbus-run-session {} &".format(self.command))


def _actions_button_event(widget):
    loginwindow.o("ui_popover_actions").popup()


def module_init():
    action_box = loginwindow.o("ui_box_actions")
    # Deprecated method
    i = 0
    while True:
        label = get("label-"+str(i), "", "actions")
        icon = get("icon-"+str(i), "", "actions")
        command = get("command-"+str(i), "", "actions")
        if label == "" or command == "":
            break
        i += 1
        button = action_button(label, icon, command)
        button.set_can_focus(False)
        action_box.add(button)
    # new method
    for section in config.sections():
        if section.startswith("button-"):
            label = get("label", "", section)
            icon = get("icon", "", section)
            command = get("command", "", section)
            button = action_button(label, icon, command)
            button.set_can_focus(False)
            action_box.add(button)
    action_box.show_all()
