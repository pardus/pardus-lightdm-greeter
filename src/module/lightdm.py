import sys
import gi
gi.require_version('LightDM', '1')
from gi.repository import LightDM


class lightdm_class:

    def __init__(self):
        self.username = ""
        self.password = ""
        self.session = ""
        self.greeter = LightDM.Greeter()
        self.msg_handler = None
        self.login_handler = None
        self.reset_page_handler = None

        self._pressed = False

        self.reset_process = False
        self.cur_password = ""
        self.new_password = ""
        self.new_password_again = ""

        self.greeter.connect("authentication-complete",
                             self.__authentication_complete_cb)
        self.greeter.connect("show_prompt", self.__show_prompt_cb)
        self.greeter.connect("show-message", self.__show_message_cb)
        self.greeter.connect_to_daemon_sync()
        self.prompt_messages = []

    def set(username=None, password=None, session=None):
        if username:
            self.username = username
        if password:
            self.password = password
        if session:
            self.session = session

    def login(self, widget=None):
        self.username = self.username.replace(" ","")
        if self.username == "root":
            if not get("allow-root-login", False, "lightdm"):
                log("lightdm: root login blocked")
                if self.msg_handler:
                    self.msg_handler(_("login as root is blocked"))
                return
        if self.greeter.get_authentication_user() != self.username:
            self.greeter.cancel_authentication()
            debug("Authentication start:"+self.username)
            self.greeter.authenticate(self.username)
        if not self._pressed:
            self._pressed = True
            self.greeter.authenticate(self.username)
            log("Login process started for {}".format(self.username))
        if self.password != "":
            self.greeter.respond(self.password)

    def __show_prompt_cb(self, greeter, text, promptType):
        debug("Prompt: "+text)
        message = text.strip()
        reset_msg=["Current password:", "New password:", "Retype new password:"]
        normal_msg = ["Password:"]
        response = ""
        if self.msg_handler:
            if message not in normal_msg+reset_msg:
                self.msg_handler(_(message))
        if message not in reset_msg:
            response = self.password
        else:
            if(self.reset_page_handler and not self.reset_process):
                self.reset_page_handler()
            if self.reset_process and self.password != "":
                self.cur_password = self.password
            if reset_msg[0] == message:
                response = self.cur_password
            elif reset_msg[1] == message:
                response = self.new_password
            elif reset_msg[2] == message:
                response = self.new_password_again
        if response == "" and self._pressed:
            return

        while self.greeter.respond(response):
            debug("Response sent")

    def __show_message_cb(self, greeter, text, message_type=None, **kwargs):
        if self.msg_handler:
            self.msg_handler(_(text.strip()))
        log(text)

    def __authentication_complete_cb(self, greeter):
        self.login()
        self._pressed = False
        debug("Authentication completed")
        error = ""
        if self.greeter.get_is_authenticated():
            if self.login_handler:
                self.login_handler()
            if self.session not in self.get_session_list() and self.session != "":
                error += _("Invalid sesion : {}").format(self.session) + "\n"
            try:
                log("Login success for {}".format(self.username))
                prestart = get("prestart","")
                loginwindow.window.hide()
                if prestart != "":
                    prestart = prestart.replace("%u",self.username)
                    prestart = prestart.replace("%s",self.session)
                    os.system(prestart)
                if not self.greeter.start_session_sync(self.session):
                    error += _("Failed to start session: {}").format(
                        self.session) + "\n"
            except:
                sys.exit(0)
        else:
            error += _("Authentication failed: {}").format(self.username)
        if error != "":
            log(error)
            if self.msg_handler:
                self.msg_handler(error)
            self.cancel()

    def get_session_list(self):
        sessions = []
        hidden_sessions = get("hidden-sessions", "", "lightdm").split(" ")
        debug("hidden-sessions: {}".format(hidden_sessions))
        for session in LightDM.get_sessions():
            if session.get_key() not in hidden_sessions:
                sessions.append(session.get_key())
        return sessions

    def get_user_list(self):
        return LightDM.UserList.get_instance().get_users()

    def is_lockscreen(self):
        if get("no-lockscreen", False, "lightdm"):
            debug("lockscreen disabled")
            return False
        return self.greeter.get_lock_hint()

    def reboot(self, widget=None):
        if LightDM.get_can_restart():
            LightDM.restart()
        else:
            error = "Failed to reboot system"
            log(error)
            if self.msg_handler:
                self.msg_handler(_(error))

    def shutdown(self, widget=None):
        if LightDM.get_can_shutdown():
            LightDM.shutdown()
        else:
            error = "Failed to shutdown system"
            log(error)
            if self.msg_handler:
                self.msg_handler(_(error))

    def cancel(self):
        self.greeter.cancel_authentication()
        self._pressed = False
        self.password=""
        self.login()


lightdm = None


def module_init():
    global lightdm
    lightdm = lightdm_class()
    if get("allow-autologin", True, "lightdm"):
        try:
            lightdm.greeter.authenticate_autologin()
        except:
            debug("autologin not configured")
