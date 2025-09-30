users = {}


class userButton(Gtk.Box):
    def __init__(self, username):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        ubut = Gtk.Button()
        self.label = Gtk.Label()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.username = username
        ubut.username = username

        ubut.set_can_focus(False)
        ubut.get_style_context().add_class("icon")
        ubut.set_relief(Gtk.ReliefStyle.NONE)
        ubut.connect("clicked", user_button_event)

        if get("show-realname", True, "userlist"):
            self.label.set_text(self.get_realname())
        else:
            self.label.set_text(username)

        box.pack_start(self.label, False, False, 0)
        ubut.add(box)
        self.pack_start(ubut, True, True, 0)

        self.show_all()
        if get("user-hide-button", True, "userlist"):
            delbut = Gtk.Button()
            delbut.get_style_context().add_class("icon")
            delbut.set_can_focus(False)
            delbut.set_relief(Gtk.ReliefStyle.NONE)
            delbut.connect("clicked", self.delete_button_event)
            img = Gtk.Image()
            img.set_from_icon_name("list-remove-symbolic", 0)
            img.set_pixel_size(12*scale)
            delbut.set_image(img)
            self.pack_end(delbut, False, False, 0)

    def get_realname(self):
        p = open("/etc/passwd", "r")
        realname = ""
        for line in p.read().split("\n"):
            if line.startswith(self.username+":"):
                realname = line.split(":")[4]
                break
        if "," in realname:
            realname = realname.split(",")[0]
        if realname == "":
            realname = self.username
        p.close()
        return realname

    def delete_button_event(self, widget):
        self.hide()
        hidden = gsettings_get("hidden-users")
        log(str(hidden))
        if self.username not in hidden.split("\n"):
            gsettings_set("hidden-users", hidden +
                          "\n{}".format(self.username))


def user_button_event(widget):
    username = widget.username
    loginwindow.o("ui_entry_search_user").set_text("")
    loginwindow.o("ui_popover_userlist").popdown()
    loginwindow.o("ui_stack_username").set_visible_child_name("show")
    loginwindow.o("ui_entry_username").set_text(username)
    loginwindow.o("ui_entry_password").grab_focus()
    loginwindow.update_username_button(username)


def show_userlist(widget):
    load_userlist()
    loginwindow.o("ui_popover_userlist").popup()


def _user_search_event(widget):
    text = widget.get_text()
    for user in users:
        if text in user:
            users[user].show_all()
        else:
            users[user].hide()


def _clear_user_search(widget, icon_pos, event):
    widget.set_text("")


_userlist_loaded = False


def load_userlist():
    global _userlist_loaded
    if _userlist_loaded:
        return
    _userlist_loaded = True
    hidden_users = get("hidden-users", "root", "userlist").split(" ") + \
        gsettings_get("hidden-users").split("\n")
    for user in lightdm.get_user_list():
        user = user.get_name()
        if user in hidden_users:
            continue
        users[user] = userButton(user)
        loginwindow.o("ui_box_userlist").add(users[user])
    loginwindow.o("ui_box_userlist").show_all()
    if len(users) < 3:
        loginwindow.o("ui_entry_search_user").hide()
    else:
        loginwindow.o("ui_entry_search_user").connect(
            "icon-press", _clear_user_search)
        loginwindow.o("ui_entry_search_user").connect(
            "changed", _user_search_event)


def module_init():
    global users
    if not get("enabled", True, "userlist"):
        loginwindow.o("ui_button_userselect").hide()
        loginwindow.o("ui_button_username").get_style_context(
        ).remove_class("button_left")
        loginwindow.o("ui_entry_username").get_style_context(
        ).remove_class("button_left")
        return

    loginwindow.o("ui_button_userselect").connect("clicked", show_userlist)
    height = int(monitor.get_common_resolution().split("x")[1])
    loginwindow.o("ui_popover_userlist").set_size_request(200, height/3)
