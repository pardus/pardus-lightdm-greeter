def _reset_password(widget=None):
    lightdm.reset_process = True
    lightdm.new_password = loginwindow.builder.get_object(
        "ui_entry_new_password1").get_text()
    lightdm.new_password_again = loginwindow.builder.get_object(
        "ui_entry_new_password2").get_text()
    lightdm.login()


def _reset_event(widget=None):
    loginwindow.builder.get_object(
        "ui_entry_reset_username").set_text(lightdm.username)
    loginwindow.main_stack.set_visible_child_name("page_reset_password")
    loginwindow.builder.get_object(
        "ui_stack_window").set_visible_child_name("main_page")


def _reset_password_entry1_event(widget):
    loginwindow.builder.get_object("ui_entry_new_password2").grab_focus()


def module_init():
    loginwindow.builder.get_object(
        "ui_button_change_password").connect("clicked", _reset_password)
    loginwindow.builder.get_object("ui_entry_new_password1").connect(
        "activate", _reset_password_entry1_event)
    loginwindow.builder.get_object("ui_entry_new_password2").connect(
        "activate", _reset_password)
    lightdm.reset_page_handler = _reset_event
