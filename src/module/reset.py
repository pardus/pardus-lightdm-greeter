
_reset_username = None
_reset_password = None


def _reset_password(widget=None):
    p1 = loginwindow.o("ui_entry_new_password1").get_text()
    p2 = loginwindow.o("ui_entry_new_password2").get_text()
    if p1 == p2:
        lightdm.set(password=_reset_password, username=_reset_username)
        lightdm.set2(password=p1, username=_reset_username)
        lightdm.login()


def _reset_event(widget=None):
    global _reset_username
    global _reset_password
    # set & backup username
    loginwindow.o("ui_entry_reset_username").set_text(lightdm.get_username())
    _reset_username = lightdm.get_username()
    _reset_password = lightdm.get_password()
    # Reset lightdm variables
    loginwindow.err_handler()
    # Change page
    loginwindow.o("ui_stack_login").set_visible_child_name(
        "page_reset_password")
    loginwindow.o("ui_stack_window").set_visible_child_name("main_page")


def _reset_password_entry1_event(widget):
    loginwindow.o("ui_entry_new_password2").grab_focus()


def module_init():
    # button
    loginwindow.o("ui_button_change_password").connect(
        "clicked", _reset_password)
    # entry enter events
    loginwindow.o("ui_entry_new_password1").connect(
        "activate", _reset_password_entry1_event)
    loginwindow.o("ui_entry_new_password2").connect(
        "activate", _reset_password)
    # handler connect
    lightdm.reset_page_handler = _reset_event
