import hashlib

############### class definition ###############


class LoginWindow:

    def __init__(self):
        self.start_windowmanager()
        self.builder = Gtk.Builder()
        self.builder.add_from_file("data/main.ui")
        self.__init_variables()
        self.__init_gui()
        self.__update_user_background_loop()
        self.__connect_signals()

    def __init_variables(self):
        self.greeter_loaded = False
        self.__blocked = False
        self.width = -1
        self.height = -1
        self.background_pixbuf = None
        self.ignore_password_cache = False

    def o(self, name=None):
        return self.builder.get_object(name)

    def __connect_signals(self):
        def block_delete(*args):
            return True

        # Main window
        self.o("ui_window_main").connect("destroy", Gtk.main_quit)
        self.o("ui_window_main").connect("delete-event", block_delete)
        self.o("ui_window_main").connect("draw", self.__draw_window)
        self.o("ui_window_main").connect(
            "focus-out-event", self.__event_window_focus_out)
        # Login button and password entry enter
        self.o("ui_button_login").connect("clicked", self.__event_login_button)
        self.o("ui_entry_password").connect(
            "activate", self.__event_login_button)
        # password entry
        self.o("ui_entry_password").connect(
            "changed", self.__event_password_entry_changed)
        # username entry
        self.o("ui_entry_username").connect(
            "activate", self.__event_username_entry_clicked)
        self.o("ui_entry_username").connect(
            "changed", self.__event_username_entry_changed)
        # password entry icons
        self.o("ui_entry_password").connect(
            "icon-press", self.password_entry_icon_press)
        self.o("ui_entry_password").connect(
            "icon-release", self.password_entry_icon_release)
        # reset entry 1
        self.o("ui_entry_new_password1").connect(
            "icon-press", self.password_entry_icon_press)
        self.o("ui_entry_new_password1").connect(
            "icon-release", self.password_entry_icon_release)
        # reset entry 2
        self.o("ui_entry_new_password2").connect(
            "icon-press", self.password_entry_icon_press)
        self.o("ui_entry_new_password2").connect(
            "icon-release", self.password_entry_icon_release)

        # username button
        self.o("ui_button_username").connect(
            "clicked", self.__event_username_button)

    def __init_gui(self):
        # Show main window and present
        self.o("ui_window_main").show()
        self.o("ui_window_main").present()
        self.o("ui_window_main").set_app_paintable(True)
        # Clear error messages
        self.o("ui_label_login_error").set_text("")
        self.o("ui_label_reset_password_error").set_text("")
        # Disable suspend options if oem stuff detected.
        if os.path.exists("/sys/firmware/acpi/tables/MSDM"):
            self.o("ui_button_sleep").hide()
        # init username if cache enabled
        if get("username-cache", True, "gtkwindow"):
            # read username from cache
            username = readfile("last-username")
            # select first username from list if empty
            if username == "":
                users = lightdm.get_user_list()
                if len(users) > 0:
                    username = users[0].get_name()
            # Start authentication
            self.o("ui_entry_username").set_text(username)
            lightdm.set(username=username)
            lightdm.greeter.authenticate(username)
            self.update_username_button(username)

############### Window event ###############

    def __event_window_focus_out(self, sender, event):
        self.o("ui_window_main").present()

    def __draw_window(self, widget, context):
        if self.background_pixbuf:
            Gdk.cairo_set_source_pixbuf(context, self.background_pixbuf, 0, 0)
            context.rectangle(0, 0, self.width, self.height)
            context.fill()

############### password entry icon events ###############

    def password_entry_icon_press(self, entry, icon_pos, event):
        entry.set_visibility(True)
        entry.set_icon_from_icon_name(1, "view-conceal-symbolic")

    def password_entry_icon_release(self, entry, icon_pos, event):
        entry.set_visibility(False)
        entry.set_icon_from_icon_name(1, "view-reveal-symbolic")

############### username button event ###############

    def __event_username_button(self, widget=None):
        self.o("ui_stack_username").set_visible_child_name("edit")
        if not lightdm.get_is_reset():
            self.o("ui_entry_username").grab_focus()

############### handlers ###############

    def err_handler(self):
        if not self.greeter_loaded:
            return
        self.unblock_gui()
        self.o("ui_entry_password").set_text("")
        self.ignore_password_cache = True
        username = lightdm.get_username()
        lightdm.reset()
        lightdm.greeter.authenticate(username)

    def msg_handler(self, message=""):
        log(message)
        self.unblock_gui()
        self.o("ui_label_login_error").set_text(message)
        self.o("ui_label_reset_password_error").set_text(message)
        self.o("ui_entry_new_password1").set_text("")
        self.o("ui_entry_new_password2").set_text("")
        self.o("ui_stack_main").set_visible_child_name("page_main")

    def login_handler(self):
        if get("password-cache", True, "gtkwindow"):
            new_hash = hashlib.sha512(
                lightdm.get_password().encode("utf-8")).hexdigest()
            writefile("{}-last-hash".format(lightdm.get_username()), new_hash)
        if get("username-cache", True, "gtkwindow"):
            writefile("last-username", lightdm.get_username())
            writefile("last-session", lightdm.get_session())

        self.kill_windowmanager()


############### events ###############

    def update_username_button(self, username):
        # Clear error messages
        self.o("ui_label_login_error").set_text("")
        self.o("ui_label_reset_password_error").set_text("")
        # Get lightdm user object
        u = LightDM.UserList.get_instance().get_user_by_name(username)
        # if object is none go edit mode
        if u != None:
            self.o("ui_stack_username").set_visible_child_name("show")
            # get real name
            realname = u.get_real_name()
            # fix realname if invalid
            if realname == None or realname == "":
                realname = username
            # set realname to username button label
            self.o("ui_button_username_label").set_label(realname)
            if not lightdm.get_is_reset():
                # password entry focus
                self.o("ui_entry_password").grab_focus()
        self.update_user_background()

    def __event_username_entry_clicked(self, widget=None):
        if not get("allow-root-login", False, "lightdm"):
            is_root = (self.o("ui_entry_username").get_text().replace(
                " ", "") == "root")
            if is_root:
                return
        self.update_username_button(lightdm.get_username())

    def __event_username_entry_changed(self, w=None):
        widget = self.o("ui_entry_username")
        # Get lightdm user object
        if not get("allow-root-login", False, "lightdm"):
            is_root = (widget.get_text().replace(" ", "") == "root")
            self.o("ui_button_login").set_sensitive(not is_root)
            self.o("ui_entry_password").set_sensitive(not is_root)
            if is_root:
                return
        # Cancel current auth and auth new user if user is valid
        lightdm.set(username=widget.get_text())
        self.err_handler()
        if not self.greeter_loaded:
            self.ignore_password_cache = False
        if lightdm.is_valid_user(widget.get_text()):
            # Update user background
            self.update_username_button(widget.get_text())
        # Update login button label
        u = LightDM.UserList.get_instance().get_user_by_name(widget.get_text())
        if u != None and u.get_logged_in():
            self.o("ui_button_login").set_label(_("Unlock"))
            self.o("ui_box_session_menu").hide()
        else:
            self.o("ui_button_login").set_label(_("Login"))
            self.o("ui_box_session_menu").show()
            
        self.o("ui_window_main").queue_draw()

    def __event_password_entry_changed(self, widget):
        # ignore if disabled
        if self.ignore_password_cache:
            return
        if not get("password-cache", True, "gtkwindow"):
            return
        # Get password from entry
        password = widget.get_text()
        # ignore if empty
        if password == "":
            return
        # get username from entry
        username = self.o("ui_entry_username").get_text()
        # read sha512sum from cache
        last_hash = readfile("{}-last-hash".format(username))
        # if hash and cache is equal run login event
        if last_hash == hashlib.sha512(password.encode("utf-8")).hexdigest():
            self.__event_login_button()

    def __event_login_button(self, widget=None):
        # ignore empty password if not allowed
        if not get("allow-empty-password", True):
            if self.o("ui_entry_password").get_text() == "":
                return
        if not get("allow-root-login", False, "lightdm"):
            is_root = (self.o("ui_entry_username").get_text().replace(
                " ", "") == "root")
            if is_root:
                return
        lightdm.set(
            self.o("ui_entry_username").get_text(),
            self.o("ui_entry_password").get_text()
        )
        # start blocking gui
        self.block_gui()
        # remove username from hidden username cache
        hidden = readfile("hidden-users")
        data = ""
        for user in hidden.split("\n"):
            if user != self.o("ui_entry_username").get_text():
                data += "{}\n".format(user)
        writefile("hidden-users", data)
        # start lightdm login
        return lightdm.login()

    def __update_user_background_loop(self):
        self.update_user_background()
        interval = 1000 * \
            int(get("background-update-interval", "0", "gtkwindow"))
        if (interval > 0):
            GLib.timeout_add(interval, self.__update_user_background_loop)

############### block - unblock gui ###############

    def unblock_gui(self):
        if not self.__blocked:
            return
        self.__blocked = False
        self.o("ui_stack_main").set_sensitive(True)
        if not lightdm.get_is_reset():
            self.o("ui_entry_password").grab_focus()
        self.o("ui_spinner_login").stop()

    def block_gui(self):
        self.__blocked = True
        self.o("ui_stack_main").set_sensitive(False)
        self.o("ui_spinner_login").start()
        # unblock after timeout
        timeout = 1000*int(get("block-gui-timeout", "10", "gtkwindow"))
        GLib.timeout_add(timeout, self.unblock_gui)

############### background update ###############

    def update_user_background(self):
        # ignore if disabled
        if get("background", "user", "gtkwindow") != "user":
            return
        # get lightdm username object
        username = self.o("ui_entry_username").get_text()
        u = LightDM.UserList.get_instance().get_user_by_name(username)
        if u != None:
            background = u.get_background()
            self.set_background(background)
        else:
            self.set_background(None)

    def set_background(self, bg=None):
        if bg == None or not os.path.isfile(bg):
            bg = appdir+"/data/bg-light.png"
            if get("dark-theme", True):
                bg = appdir+"/data/bg-dark.png"
            if os.path.exists("/etc/alternatives/desktop-theme/login/background.svg"):
                bg = "/etc/alternatives/desktop-theme/login/background.svg"
        if os.path.isfile(bg):
            try:
                py = GdkPixbuf.Pixbuf.new_from_file(bg)
                if self.width / int(scale) > 0:
                    px = py.scale_simple(
                        self.width / int(scale), self.height / int(scale), GdkPixbuf.InterpType.BILINEAR)
                if px and self.background_pixbuf != px:
                    self.background_pixbuf = px
            except Exception as e:
                print(str(e))
        GLib.idle_add(self.o("ui_window_main").queue_draw)

############### css load ###############

    def load_css(self):
        css = open(
            "/usr/share/pardus/pardus-lightdm-greeter/data/main.css", "r").read()
        if get("dark-theme", True):
            css += open("/usr/share/pardus/pardus-lightdm-greeter/data/colors-dark.css").read()
        else:
            css += open("/usr/share/pardus/pardus-lightdm-greeter/data/colors.css").read()
        cssprovider.load_from_data(bytes(css, "UTF-8"))


############### logo update ###############


    def set_logo(self, logo):
        if os.path.isfile(logo):
            self.o("ui_image_logo").set_from_file(logo)
        else:
            self.o("ui_image_logo").set_from_file(None)

############### resolution sync ###############

    def sync_resolution(self):
        self.o("ui_window_main").resize(
            self.width / int(scale), self.height / int(scale))
        self.o("ui_window_main").set_size_request(
            self.width / int(scale), self.height / int(scale))
        self.o("ui_window_main").fullscreen()
        self.o("ui_window_main").set_resizable(False)
        self.background_pixbuf = None
        if "user" == get("background", "user", "gtkwindow"):
            self.update_user_background()
        else:
            self.set_background(get("background", "user", "gtkwindow"))
        self.o("ui_popover_userlist").set_size_request(250, self.height/3)

############### windowmanager ###############

    def start_windowmanager(self):
        wm = get("window-manager", "xfwm4")
        if which(wm.split(" ")[0]):
            subprocess.run(["{} 2>/dev/null &".format(wm)], shell=True)

    def kill_windowmanager(self):
        wm = get("window-manager", "xfwm4")
        if which(wm.split(" ")[0]):
            subprocess.run(["killall {}".format(wm)], shell=True)



############### class end ###############


loginwindow = None
screen = None
cursor = None
cssprovider = None

############### module init ###############
def module_init():
    global loginwindow
    global screen
    global cssprovider
    global cursor

    # create class
    loginwindow = LoginWindow()
    # screen init
    screen = loginwindow.o("ui_window_main").get_screen()
    cssprovider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    cursor = Gdk.Cursor(Gdk.CursorType.LEFT_PTR)
    if get("fix-cursor", False, "gtkwindow"):
        Gdk.Screen.get_root_window(screen).set_cursor(cursor)
    else:
        loginwindow.o("ui_window_main").get_window().set_cursor(cursor)
    style_context.add_provider_for_screen(
        screen, cssprovider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    # connect handlers
    lightdm.msg_handler = loginwindow.msg_handler
    lightdm.err_handler = loginwindow.err_handler
    lightdm.login_handler = loginwindow.login_handler
    # set logo
    loginwindow.set_logo(get("logo", "", "gtkwindow"))
    # load css
    loginwindow.load_css()
