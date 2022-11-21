class action_button(Gtk.Button):
    def __init__(self, label, command):
        super().__init__()
        self.command = command
        self.connect("clicked", self.run)
        self.label = Gtk.Label()
        self.label.set_text("  "+label)
        self.set_relief(Gtk.ReliefStyle.NONE)
        box = Gtk.Box()
        box.pack_start(self.label, False, False, 0)
        box.show_all()
        self.add(box)
        self.show_all()

    def run(self, widget):
        os.system(self.command+" &")


def _actions_button_event(widget):
    loginwindow.builder.get_object("ui_popover_actions").popup()


def module_init():
    i = 0
    action_box = loginwindow.builder.get_object("ui_box_actions")

    while True:
        label = get("label-"+str(i), "", "actions")
        command = get("command-"+str(i), "", "actions")
        if label == "" or command == "":
            break
        i += 1
        button = action_button(label, command)
        action_box.add(button)
        action_box.show_all()
    button = loginwindow.builder.get_object("ui_button_actionsmenu")
    if i == 0:
        button.hide()
    else:
        button.connect("clicked", _actions_button_event)
        button.show_all()
