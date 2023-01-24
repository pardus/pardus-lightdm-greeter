users = {}

class userButton(Gtk.Box):
    def __init__(self, username):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self.label = Gtk.Button()
        self.label.set_can_focus(False)
        self.label.get_style_context().add_class("icon")
        self.label.username = username
        self.label.set_alignment(0,self.label.get_alignment()[1])
        if get("show-realname", True, "userlist"):
            self.label.set_label(self.get_realname())
        else:
            self.label.set_label(username)
        self.pack_start(self.label,True,True,0)
        self.show_all()
        self.label.set_relief(Gtk.ReliefStyle.NONE)
        self.label.connect("clicked", user_button_event)
        if get("user-hide-button",True,"userlist"):
            delbut = Gtk.Button()
            delbut.get_style_context().add_class("icon")
            delbut.set_can_focus(False)
            delbut.set_relief(Gtk.ReliefStyle.NONE)
            delbut.connect("clicked",self.delete_button_event)
            img = Gtk.Image()
            img.set_from_icon_name("list-remove-symbolic",Gtk.IconSize.MENU)
            delbut.set_image(img)
            self.pack_end(delbut,False,False,0)

    def get_realname(self):
        p = open("/etc/passwd", "r")
        realname = ""
        for line in p.read().split("\n"):
            if line.startswith(self.label.username+":"):
                realname = line.split(":")[4]
                break
        if realname.endswith(",,,"):
            realname = realname[:-3]
        if realname == "":
            realname = self.label.username
        p.close()
        return realname

    def delete_button_event(self, widget):
        self.hide()
        hidden = readfile("hidden-users")
        log(str(hidden))
        if self.label.username not in hidden.split("\n"):
            writefile("hidden-users",hidden+"\n{}".format(self.label.username))


def user_button_event(widget):
    username = widget.username
    loginwindow.o("ui_entry_search_user").set_text("")
    loginwindow.o("ui_popover_userlist").popdown()
    loginwindow.err_handler()
    loginwindow.o("ui_entry_username").set_text(username)
    lightdm.set(username = username)
    lightdm.login()
    loginwindow.o("ui_entry_password").grab_focus()

def show_userlist(entry, icon_pos, event):
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
    hidden_users = get("hidden-users", "root", "userlist").split(" ") + readfile("hidden-users").split("\n")
    for user in lightdm.get_user_list():
        print(user.get_layouts(), file=sys.stderr)
        user = user.get_name()
        if user in hidden_users:
            continue
        users[user] = userButton(user)
        loginwindow.o("ui_box_userlist").add(users[user])
    loginwindow.o("ui_box_userlist").show_all()
    if len(users) < 3:
        loginwindow.o("ui_entry_search_user").hide()
    else:
        loginwindow.o("ui_entry_search_user").connect("icon-press", _clear_user_search)
        loginwindow.o("ui_entry_search_user").connect("changed", _user_search_event)

def module_init():
    global users
    if not get("enabled", True, "userlist"):
        loginwindow.o("ui_entry_username").set_icon_sensitive(1, False)
        loginwindow.o("ui_entry_username").set_icon_from_pixbuf(None)
        return

    loginwindow.o("ui_entry_username").connect("icon-press", show_userlist)
    height = int(monitor.get_common_resolution().split("x")[1])
    loginwindow.o("ui_popover_userlist").set_size_request(150, height/3)

