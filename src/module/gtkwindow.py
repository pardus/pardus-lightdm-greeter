import hashlib

############### class definition ###############


class LoginWindow:

    def __init__(self):
        self.start_windowmanager()
        self.builder = Gtk.Builder()
        self.builder.add_from_file("data/main.ui")
        self.o = self.builder.get_object
        self.__init_variables()
        self.__init_gui()
        self.__update_user_background_loop()
        self.__connect_signals()
        self.__last_hash = gsettings_get("last-hash").split("\n")
        self.set_background()

    def __init_variables(self):
        self.image_status = True
        self.greeter_loaded = False
        self.__blocked = False
        self.width = -1
        self.height = -1
        self.background_pixbuf = None
        self.ignore_password_cache = False
        self.background_handler = None

    def __connect_signals(self):
        def block_delete(*args):
            return True

        # Main window
        self.o("ui_window_main").connect("destroy", Gtk.main_quit)
        self.o("ui_window_main").connect("delete-event", block_delete)
        # Login button and password entry enter
        self.o("ui_button_login").connect("clicked", self.event_login_button)
        self.o("ui_entry_password").connect(
            "activate", self.event_login_button)
        # password entry
        self.o("ui_entry_password").connect(
            "changed", self.__event_password_entry_changed)
        self.o("ui_entry_password").connect(
            "focus-in-event", self.__screen_keyboard_event)
        self.o("ui_entry_password").connect(
            "button_press_event", self.__screen_keyboard_event)
        # username entry
        self.o("ui_entry_username").connect(
            "activate", self.__event_username_entry_clicked)
        self.o("ui_entry_username").connect(
            "changed", self.__event_username_entry_changed)
        self.o("ui_entry_username").connect(
            "focus-in-event", self.__screen_keyboard_event)
        self.o("ui_entry_username").connect(
            "button_press_event", self.__screen_keyboard_event)
        # password entry icons
        self.o("ui_button_eye").connect(
            "button_press_event", self.password_entry_button_press)
        self.o("ui_button_eye").connect(
            "button_release_event", self.password_entry_button_release)
        # reset entry 1
        self.o("ui_entry_new_password1").connect(
            "icon-press", self.password_entry_icon_press)
        self.o("ui_entry_new_password1").connect(
            "icon-release", self.password_entry_icon_release)
        self.o("ui_entry_new_password1").connect(
            "focus-in-event", self.__screen_keyboard_event)

        # reset entry 2
        self.o("ui_entry_new_password2").connect(
            "icon-press", self.password_entry_icon_press)
        self.o("ui_entry_new_password2").connect(
            "icon-release", self.password_entry_icon_release)
        self.o("ui_entry_new_password2").connect(
            "focus-in-event", self.__screen_keyboard_event)

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
        username = ""
        if get("username-cache", True, "gtkwindow"):
            # read username from cache
            username = gsettings_get("last-username")

        # select first username from list if empty
        if username == "":
            users = lightdm.get_user_list()
            if len(users) > 0:
                username = users[0].get_name()
        # Start authentication
        self.o("ui_entry_username").set_text(username)
        lightdm.set(username=username)
        self.update_username_button(username)
        if get("authenticate-on-start", True, "gtkwindow"):
            lightdm.greeter.authenticate(username)

############### Window event ###############

    def __screen_keyboard_event(self, event, data):
        if get("touch-mode", False):
            os.system(get("screen-keyboard", "onboard", "keyboard")+"&")


############### password entry icon events ###############

    def password_entry_icon_press(self, entry, icon_pos, event):
        entry.set_visibility(True)
        entry.set_icon_from_icon_name(1, "view-conceal-symbolic")

    def password_entry_icon_release(self, entry, icon_pos, event):
        entry.set_visibility(False)
        entry.set_icon_from_icon_name(1, "view-reveal-symbolic")

    def password_entry_button_press(self, widget=None, event=None):
        self.o("ui_entry_password").set_visibility(True)
        self.o("ui_icon_eye").set_from_icon_name("view-conceal-symbolic", 0)

    def password_entry_button_release(self, widget=None, event=None):
        self.o("ui_entry_password").set_visibility(False)
        self.o("ui_icon_eye").set_from_icon_name("view-reveal-symbolic", 0)

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
        if get("authenticate-on-start", True, "gtkwindow"):
            lightdm.greeter.authenticate(username)

    def msg_handler(self, message=""):
        log(message)
        self.unblock_gui()
        self.o("ui_label_login_error").set_text(message)
        self.o("ui_label_reset_password_error").set_text(message)
        self.o("ui_entry_new_password1").set_text("")
        self.o("ui_entry_new_password2").set_text("")
        self.o("ui_stack_login").set_visible_child_name("page_main")

    def login_handler(self):
        if get("password-cache", True, "gtkwindow"):
            username = lightdm.get_username()
            new_hash = hashlib.sha512(
                lightdm.get_password().encode("utf-8")).hexdigest()

            new_last_hash = username+"="+new_hash+"\n"
            for h in self.__last_hash:
                if h.startswith(username+"="):
                    continue
            gsettings_set("last-hash", new_last_hash.strip())
        if get("username-cache", True, "gtkwindow"):
            gsettings_set("last-username", lightdm.get_username())

        busdir = "/var/lib/lightdm/"
        if os.path.exists("/{}/pardus-greeter".format(busdir)):
            os.unlink("/{}/pardus-greeter".format(busdir))

        self.kill_windowmanager()
        self.o("ui_window_main").hide()


############### events ###############

    def update_username_button(self, username):
        # Clear error messages
        self.o("ui_label_login_error").set_text("")
        self.o("ui_label_reset_password_error").set_text("")
        # Get lightdm user object
        u = LightDM.UserList.get_instance().get_user_by_name(username)
        # if object is none go edit mode
        if u is not None:
            self.update_user_background()
            self.o("ui_stack_username").set_visible_child_name("show")
            # get real name
            realname = u.get_real_name()
            # fix realname if invalid
            if realname is None or realname == "":
                realname = username
            # set realname to username button label
            self.o("ui_button_username_label").set_label(realname)
            if not lightdm.get_is_reset():
                # password entry focus
                self.o("ui_entry_password").grab_focus()
            if u.get_logged_in():
                self.o("ui_button_login").set_label(_("Unlock"))
                self.o("ui_box_session_menu").hide()
            else:
                self.o("ui_button_login").set_label(_("Login"))
                self.o("ui_box_session_menu").show()
        else:
            self.o("ui_button_login").set_label(_("Login"))
            self.o("ui_box_session_menu").show()

    def __event_username_entry_clicked(self, widget=None):
        if not get("allow-root-login", False, "lightdm"):
            is_root = (self.o("ui_entry_username").get_text().replace(
                " ", "") == "root")
            if is_root:
                return
        if not lightdm.get_is_reset():
            self.o("ui_entry_password").grab_focus()
        self.__event_username_entry_changed(widget)

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
        if not self.greeter_loaded:
            self.ignore_password_cache = False
        if lightdm.is_valid_user(widget.get_text()):
            if get("authenticate-on-start", True, "gtkwindow"):
                lightdm.reset()
                lightdm.greeter.authenticate(widget.get_text())
        # Update username button
        self.update_username_button(widget.get_text())

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
        last_hash = None
        for h in self.__last_hash:
            if h.startswith(username+"="):
                last_hash = h[len(username)+1:]
                break
        # if hash and cache is equal run login event
        if last_hash == hashlib.sha512(password.encode("utf-8")).hexdigest():
            self.event_login_button()

    def event_login_button(self, widget=None):
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
        hidden = gsettings_get("hidden-users")
        data = ""
        for user in hidden.split("\n"):
            if user != self.o("ui_entry_username").get_text():
                data += "{}\n".format(user)
        gsettings_set("hidden-users", data)
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
        debug("Block GUI")
        self.o("ui_stack_login").set_sensitive(True)
        if not lightdm.get_is_reset():
            self.o("ui_entry_password").grab_focus()
        self.o("ui_spinner_login").stop()

    def block_gui(self):
        self.__blocked = True
        debug("Unblock GUI")
        self.o("ui_stack_login").set_sensitive(False)
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
        if u is not None:
            background = u.get_background()
            th = threading.Thread(
                target=self.set_background, args=[background])
        else:
            th = threading.Thread(target=self.set_background, args=[None])

        th.start()

    def set_background(self, bg=None):
        if bg is None or not os.path.isfile(bg):
            bg = appdir+"/data/bg-light.png"
            if get("dark-theme", True):
                bg = appdir+"/data/bg-dark.png"
            if os.path.exists("/etc/alternatives/desktop-theme/login/background.svg"):
                bg = "/etc/alternatives/desktop-theme/login/background.svg"
        if os.path.isfile(bg):
            try:
                py = GdkPixbuf.Pixbuf.new_from_file(bg)
                px = None
                if self.width > 0:
                    px = py.scale_simple(
                        self.width, self.height, GdkPixbuf.InterpType.BILINEAR)
                if px is not None and self.background_pixbuf != px:
                    self.background_pixbuf = px
            except Exception as e:
                print(traceback.format_exc(), file=sys.stderr)
        if self.background_handler is not None:
            self.background_pixbuf = self.background_handler(
                self.background_pixbuf)
        GLib.idle_add(self.draw_background)

    def draw_background(self):
        if self.image_status:
            self.o("ui_image_2").set_from_pixbuf(self.background_pixbuf)
            self.o("ui_stack_image").set_visible_child_name("image2")
        else:
            self.o("ui_image_1").set_from_pixbuf(self.background_pixbuf)
            self.o("ui_stack_image").set_visible_child_name("image1")
        self.image_status = not self.image_status

    def apply_scale(self):
        # buttons 64px
        for but in ["ui_icon_stack_restart", "ui_icon_stack_poweroff", "ui_icon_stack_sleep"]:
            self.o(but).set_pixel_size(64*scale)
        # buttons 36 px
        for but in ["ui_icon_message", "ui_icon_wifi", "ui_icon_network", "ui_icon_powermenu",
                    "ui_icon_options", "ui_icon_capslock", "ui_icon_numlock"]:
            self.o(but).set_pixel_size(36*scale)
        # buttons 12px
        for but in ["ui_icon_userselect", "ui_icon_keyboard_layout", "ui_icon_default_session",
                    "ui_icon_virtual_keyboard", "ui_icon_poweroff", "ui_icon_reboot", "ui_icon_eye",
                    "ui_icon_sleep", "ui_icon_keyboard_layout_dd", "ui_icon_default_session_dd"]:
            self.o(but).set_pixel_size(12*scale)
        # login box width
        self.o("ui_box_reset_passwd").set_size_request(250*scale, -1)
        self.o("ui_box_login").set_size_request(250*scale, -1)
        # login button & entry 128 x 31
        for but in ["ui_button_login", "ui_box_username", "ui_entry_reset_username", "ui_entry_password",
                    "ui_box_password",
                    "ui_entry_new_password1", "ui_entry_new_password2", "ui_box_reset_buttons"]:
            self.o(but).set_size_request(128*scale, 31*scale)
        # user list
        self.o("ui_box_userlist_main").set_size_request(
            250*scale, self.height/3)
        self.o("ui_popover_userlist").set_size_request(
            250*scale, self.height/3)

############### css load ###############

    def load_css(self):
        css = open(
            "/usr/share/pardus/pardus-lightdm-greeter/data/main.css", "r").read()
        if get("dark-theme", True):
            css += open("/usr/share/pardus/pardus-lightdm-greeter/data/colors-dark.css").read()
        else:
            css += open("/usr/share/pardus/pardus-lightdm-greeter/data/colors.css").read()
        cssprovider.load_from_data(bytes(self.scale_css(css, scale), "UTF-8"))

    def scale_css(self, ctx, ratio):
        ret = ""
        for token in ctx.split(" "):
            if "px" in token:
                pix = int(token.split("px")[0].strip())
                token = str(ratio*pix)+"px"+token.split("px")[1]
            ret += (token+" ")
        return ret.strip()

############### logo update ###############

    def set_logo(self, logo):
        if os.path.isfile(logo):
            self.o("ui_image_logo").set_from_file(logo)
        else:
            self.o("ui_image_logo").set_from_file(None)

############### resolution sync ###############

    def sync_resolution(self):
        self.o("ui_window_main").resize(
            self.width, self.height)
        self.o("ui_window_main").set_size_request(
            self.width, self.height)
        self.o("ui_window_main").fullscreen()
        self.o("ui_window_main").set_resizable(False)
        self.background_pixbuf = None
        if "user" == get("background", "user", "gtkwindow"):
            self.update_user_background()
        else:
            self.set_background(get("background", "user", "gtkwindow"))
        self.apply_scale()

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
