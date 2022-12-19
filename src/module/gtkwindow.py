import hashlib


class LoginWindow:

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("data/main.ui")
        self.width = -1
        self.height = -1
        self._define_objects()
        self._connect_signal()
        self.msg_handler()
        self.background_pixbuf = None
        self.bg_old = ""
        username = readfile("last-username")
        if get("username-cache", True, "gtkwindow"):
            if username == "":
                username = lightdm.get_user_list()[0].get_name().replace(" ","")
            self.username_entry.set_text(username)
            lightdm.username = username
            self._username_entry_event(self.username_entry)
            u = LightDM.UserList.get_instance().get_user_by_name(username)
            if u:
                realname = u.get_real_name()
                if realname == None or realname == "":
                    realname = username
                self.builder.get_object("ui_button_username_label").set_label(realname)
                self.password_entry.grab_focus()
            else:
                self.builder.get_object("ui_stack_username").set_visible_child_name("edit")
        else:
            self.builder.get_object("ui_stack_username").set_visible_child_name("edit")
        debug("Username cache loaded {}".format(username))
        self.window.present()
        self.window.set_keep_above(True)
        self.window.connect("focus-out-event", self.on_focus_out)
        self.window.connect("draw",self.draw)
        if "user" == get("background", "user", "gtkwindow"):
            self._username_entry_event_changed(self.username_entry)
        lightdm.login()
        GLib.idle_add(self.__update_user_background_loop)

    def on_focus_out(self, sender, event):
        self.window.present()

    def _define_objects(self):
        self.window = self.builder.get_object("ui_window_main")
        self.loginscreen = self.builder.get_object("ui_box_loginscreen")
        self.main_stack = self.builder.get_object("ui_stack_main")
        self.login_button = self.builder.get_object("ui_button_login")
        self.password_entry = self.builder.get_object("ui_entry_password")
        self.username_entry = self.builder.get_object("ui_entry_username")
        self.username_button = self.builder.get_object("ui_button_username")
        self.error_message = self.builder.get_object("ui_label_login_error")
        self.error_message_reset = self.builder.get_object("ui_label_reset_password_error")
        self.userlist = self.builder.get_object("ui_popover_userlist")
        self.userbox = self.builder.get_object("ui_box_userlist")
        self.user_search = self.builder.get_object("ui_entry_search_user")
        self.logo = self.builder.get_object("ui_image_logo")

    def _connect_signal(self):
        self.window.connect("destroy", Gtk.main_quit)
        self.login_button.connect("clicked", self._login_button_event)
        # Password entry event
        self.password_entry.connect("activate", self._login_button_event)
        self.username_entry.connect("activate", self._username_entry_event)
        if get("password-cache", True, "gtkwindow"):
            self.password_entry.connect("changed", self._password_entry_event)
        self.username_entry.connect("changed", self._username_entry_event_changed)

        # Entry icons event
        self.password_entry.connect("icon-press", self.__view_password_text)
        self.password_entry.connect("icon-release", self.__hide_password_text)
        def edit_mode(widget):
            self.builder.get_object("ui_stack_username").set_visible_child_name("edit")
            self.username_entry.grab_focus()
        self.username_button.connect("clicked",edit_mode)

    def _username_entry_event(self, widget):
        self.password_entry.grab_focus()

    def _username_entry_event_changed(self,widget):
        u = LightDM.UserList.get_instance().get_user_by_name(widget.get_text())
        if u != None and lightdm.greeter.get_in_authentication():
            lightdm.cancel()
            self.reset_messages()
            lightdm.username = widget.get_text()
            lightdm.login()
        self.update_user_background()

    def update_user_background(self):
        u = LightDM.UserList.get_instance().get_user_by_name(lightdm.username)
        if u != None and "user" == get("background", "user", "gtkwindow"):
            background = u.get_background()
            self.set_background(background)

    def __view_password_text(self, entry, icon_pos, event):
        entry.set_visibility(True)
        entry.set_icon_from_icon_name(1, "view-conceal-symbolic")
        debug("Password visible: True")

    def __hide_password_text(self, entry, icon_pos, event):
        entry.set_visibility(False)
        entry.set_icon_from_icon_name(1, "view-reveal-symbolic")
        debug("Password visible: False")

    def _password_entry_event(self, widget):
        if not get("password-cache", True, "gtkwindow"):
            return
        password = widget.get_text()
        username = self.username_entry.get_text().replace(" ","")
        last_hash = readfile("{}-last-hash".format(username))
        if last_hash == hashlib.sha512(password.encode("utf-8")).hexdigest():
            debug("Password cache event: {} / {}".format(username, "*"*len(password)))
            self._login_button_event(widget)

    def msg_handler(self, message=""):
        log(message)
        self.unblock_gui()
        self.error_message.set_text(message)
        self.error_message_reset.set_text(message)
        self.password_entry.set_text("")
        lightdm.password=""
        self.builder.get_object("ui_entry_new_password1").set_text("")
        self.builder.get_object("ui_entry_new_password2").set_text("")

    def unblock_gui(self):
        self.main_stack.set_sensitive(True)
        self.password_entry.grab_focus()
        self.builder.get_object("ui_spinner_login").stop()

    def block_gui(self):
        self.main_stack.set_sensitive(False)
        self.builder.get_object("ui_spinner_login").start()
        timeout = 1000*int(get("block-gui-timeout", "10", "gtkwindow"))
        GLib.timeout_add(timeout,self.unblock_gui)

    def reset_messages(self):
        self.error_message.set_text("")
        self.error_message_reset.set_text("")

    def _login_button_event(self, widget):
        lightdm.password = self.password_entry.get_text()
        if lightdm.password == "" and not get("allow-empty-password",True):
            return
        self.block_gui()
        lightdm.username = self.username_entry.get_text().replace(" ","")
        hidden = readfile("hidden-users")
        data = ""
        for user in hidden.split("\n"):
            if user != lightdm.username:
                data += "{}\n".format(user)
        writefile("hidden-users",data)
        debug("Login button event: {} / {}".format(lightdm.username, "*"*len(lightdm.password)))
        return lightdm.login()

    def login_event(self):
        if get("password-cache", True, "gtkwindow"):
            new_hash = hashlib.sha512(
                lightdm.password.encode("utf-8")).hexdigest()
            writefile("{}-last-hash".format(lightdm.username), new_hash)
        writefile("last-username", lightdm.username)
        writefile("last-session", lightdm.session)

    def draw(self, widget, context):
        if self.background_pixbuf:
            Gdk.cairo_set_source_pixbuf(context, self.background_pixbuf, 0, 0)
            context.paint()

    def set_background(self, bg=None):
        if bg == None or not os.path.isfile(bg):
            bg = appdir+"/data/bg-light.png"
            if get("dark-theme", True):
                bg = appdir+"/data/bg-dark.png"
        if os.path.isfile(bg):
            try:
                py = GdkPixbuf.Pixbuf.new_from_file_at_scale(bg,self.width/scale, self.height/scale,True)
                px = py.scale_simple(self.width/scale, self.height/scale, GdkPixbuf.InterpType.BILINEAR)
                if px and self.background_pixbuf != px:
                    self.background_pixbuf = px
                    self.window.queue_draw()
            except:
                return

    def load_css(self):
        css = open("/usr/share/pardus/pardus-greeter/data/main.css", "r").read()
        if get("dark-theme", True):
            css += open("/usr/share/pardus/pardus-greeter/data/colors-dark.css").read()
        else:
            css += open("/usr/share/pardus/pardus-greeter/data/colors.css").read()
        cssprovider.load_from_data(bytes(css, "UTF-8"))

    def set_logo(self,logo):
        if os.path.isfile(logo):
            loginwindow.logo.set_from_file(logo)
        else:
            loginwindow.logo.set_from_file(None)

    def sync_resolution(self):
        self.window.resize(self.width/scale, self.height/scale)
        self.window.set_size_request(self.width/scale, self.height/scale)
        self.background_pixbuf = None
        if "user" == get("background", "user", "gtkwindow"):
            self.update_user_background()
        else:
            self.set_background(get("background", "user", "gtkwindow"))

    def __update_user_background_loop(self):
        self.update_user_background()
        interval = 1000*int(get("background-update-interval", "0", "gtkwindow"))
        if(interval > 0):
            GLib.timeout_add(interval, self.__update_user_background_loop)

loginwindow = None
screen = None
cssprovider = None
cursor = None

def module_init():
    global loginwindow
    global screen
    global cssprovider
    global cursor

    loginwindow = LoginWindow()
    screen = loginwindow.window.get_screen()
    cursor = Gdk.Cursor(Gdk.CursorType.LEFT_PTR)
    cssprovider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    Gdk.Screen.get_root_window(screen).set_cursor(cursor)
    style_context.add_provider_for_screen(
        screen, cssprovider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    lightdm.msg_handler = loginwindow.msg_handler
    lightdm.login_handler = loginwindow.login_event
    logo = get("logo", "", "gtkwindow")
    loginwindow.set_logo(logo)
    loginwindow.load_css()
