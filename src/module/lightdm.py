import sys

import gi
gi.require_version('LightDM', '1')
from gi.repository import LightDM

############### class definition ###############


class lightdm_class:

    def __init_variables(self):
        # variables
        self.__username = None
        self.__password = None
        self.__session = None
        self.__is_reset = False
        self.__last_prompt = None
        # password reset variables
        self.__password_new = None
        # Handlers
        self.msg_handler = None
        self.err_handler = None
        self.login_handler = None
        self.reset_page_handler = None
        # Messages
        self.__reset_messages = ["Current password:",
                                 "New password:", "Retype new password:"]
        self.__prompt_messages = ["Password:"]
        # lists
        self.__ulist = None
        self.__slist = None

    def __init__(self):
        self.greeter = LightDM.Greeter()
        self.__init_variables()
        self.__connect_signals()

    def __connect_signals(self):
        self.greeter.connect("authentication-complete",
                             self.__authentication_complete)
        self.greeter.connect("show_prompt", self.__show_prompt)
        self.greeter.connect("show-message", self.__show_message)
        self.greeter.connect_to_daemon_sync()

############### set - reset - login ###############

    def set(self, username=None, password=None, session=None):
        """Set greeter variables"""
        if username is not None:
            self.__username = username.replace(" ", "")
        if password is not None:
            self.__password = password
        if session is not None:
            self.__session = session

    def set2(self, username=None, password=None):
        """Set reset password variables"""
        if username is not None:
            self.__username = username
        if password is not None:
            self.__password_new = password

    def get_username(self):
        """get current username"""
        if self.__username is None:
            return ""
        return self.__username

    def get_session(self):
        """get current session"""
        if self.__session is None:
            return ""
        return self.__session

    def get_is_reset(self):
        """get reset status"""
        return self.__is_reset

    def get_password(self):
        """get current session"""
        if self.__password_new is not None:
            return self.__password_new
        if self.__password is None:
            return ""
        return self.__password

    def reset(self):
        """Remove variables and cancel authentication"""
        if self.greeter.get_in_authentication():
            self.greeter.cancel_authentication()
        self.__username = None
        self.__password = None
        self.__is_reset = False
        self.__password_new = None

    def login(self):
        """Main login button event"""
        self.write_values("Login:")
        if self.__username is None:
            return
        if self.__username == "root" and not get("allow-root-login", False, "lightdm"):
            return
        if self.__password is None:
            return
        if self.greeter.get_authentication_user() != self.__username:
            debug("Auth user changed: {} -> {}".format(self.greeter.get_authentication_user(), self.__username))
            self.greeter.cancel_authentication()
        elif self.greeter.get_in_authentication():
            if not self.__is_reset and self.__last_prompt is not None:
                self.greeter.respond(self.__password)
                return
            # First cancel if authenticated user is not target user
            self.greeter.cancel_authentication()
        # Start authentication
        self.greeter.authenticate(self.__username)


############### lightdm greeter functions ###############

    def __show_prompt(self, greeter, text, promptType):
        """Prompt function"""
        self.__last_prompt = text.strip()
        debug("Prompt: {} ({})".format(text.strip(), self.__is_reset))
        self.write_values("Show Prompt:")
        if self.__is_reset:
            # create response variable
            response = None
            # set response from prompt message
            if text.strip() == "Current password:":
                response = self.__password
            elif text.strip() == "Password:":
                response = self.__password
            else:
                response = self.__password_new
            # Send response
            if response is not None:
                self.greeter.respond(response)
        else:
           # Check password reset required.
            if text.strip() in self.__reset_messages:
                # Trigger reset handler
                if self.reset_page_handler is not None:
                    self.reset_page_handler()
                # Set reset value
                self.__is_reset = True
                # then exit function
                return
            # Respond with password
            elif text.strip() in self.__prompt_messages:
                if self.__password is None:
                    return
                self.greeter.respond(self.__password)
            # Unknown prompts.
            else:
                self.__show_message(greeter, text)

    def __show_message(self, greeter, text, message_type=None, **kwargs):
        """Message function"""
        # Send message to message handler
        if self.msg_handler:
            self.msg_handler(_(text.strip()))

    def __authentication_complete(self, greeter):
        """After auth function"""
        self.__last_prompt = None
        # Check authentication successfully
        if self.greeter.get_is_authenticated():
            # Trigger login handler
            if self.login_handler:
                self.login_handler()
            # Check session is valid
            if self.__session is None:
                self.__session = ""
            if self.__session == "":
                self.__session = self.get_session_list()[0]
            if self.__session not in self.get_session_list():
                self.__show_message(greeter, _(
                    "Invalid session : {}").format(self.__session))
                self.__session = ""
            try:
                # Start session
                if not self.greeter.start_session_sync(self.__session):
                    self.__show_message(greeter, _(
                        "Failed to start session: {}").format(self.__session))
            except:
                # Exit greeter (for reload)
                sys.exit(0)
            debug("Greeter done")
            sys.exit(0)
        else:
            # Authentication failed.
            self.__show_message(greeter, _(
                "Authentication failed: {}").format(self.__username))
            # Reset variables and cancel authentication
            if self.err_handler:
                self.err_handler()

############### Extra functions ###############

    def write_values(self, msg):
        debug(msg)
        debug("   Username: {}".format(self.__username))
        debug("   Password: {}".format(self.__password))
        debug("   Session: {}".format(self.__session))
        debug("   Is reset: {}".format(self.__is_reset))
        debug("   New password: {}".format(self.__password_new))
        debug("   In User: {}".format(self.greeter.get_authentication_user()))
        debug("   In Auth: {}".format(self.greeter.get_in_authentication()))

    @cached
    def get_session_list(self):
        if self.__slist is None:
            self.__slist = []
            hidden_sessions = ["lightdm-xsession"] + \
                get("hidden-sessions", "", "lightdm").split(" ")
            debug("hidden-sessions: {}".format(hidden_sessions))
            for session in LightDM.get_sessions():
                if get("ignore-wayland", False, "lightdm"):
                    if session.get_session_type() == "wayland":
                        continue
                if session.get_key() not in hidden_sessions:
                    self.__slist.append(session.get_key())
        return self.__slist

    def is_valid_user(self, name):
        for u in self.get_user_list():
            if name == u.get_name():
                return True
        return False

    @cached
    def get_user_list(self):
        uids = []
        self.__ulist = []
        for u in LightDM.UserList.get_instance().get_users():
            if u.get_uid() in uids or u.get_uid() < 1000:
                continue
            uids.append(u.get_uid())
            self.__ulist.append(u)
        return self.__ulist

    def is_lockscreen(self):
        if get("no-lockscreen", False, "lightdm"):
            debug("lockscreen disabled")
            return False
        return self.greeter.get_lock_hint()

    def reboot(self, widget=None):
        if LightDM.get_can_restart():
            LightDM.restart()
        else:
            if self.msg_handler:
                self.msg_handler(_("Failed to reboot system"))

    def sleep(self, widget=None):
        if LightDM.get_can_suspend():
            LightDM.suspend()
        else:
            if self.msg_handler:
                self.msg_handler(_("Failed to sleep system"))

    def shutdown(self, widget=None):
        if LightDM.get_can_shutdown():
            LightDM.shutdown()
        else:
            if self.msg_handler:
                self.msg_handler(_("Failed to shutdown system"))

############### end of class ###############


lightdm = None


def module_init():
    global lightdm
    lightdm = lightdm_class()
    if get("allow-autologin", True, "lightdm"):
        try:
            lightdm.greeter.authenticate_autologin()
        except:
            debug("autologin not configured")
