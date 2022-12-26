def _options_event(widget):
    loginwindow.builder.get_object("ui_revealer_default_session").set_reveal_child(False)
    loginwindow.builder.get_object("ui_revealer_keyboard_layout").set_reveal_child(False)
    loginwindow.builder.get_object("ui_icon_default_session_dd").set_from_icon_name("go-next-symbolic", 0)
    loginwindow.builder.get_object("ui_icon_keyboard_layout_dd").set_from_icon_name("go-next-symbolic", 0)
    loginwindow.builder.get_object("ui_popover_options").popup()

def _powermenu_event(widget):
    loginwindow.builder.get_object("ui_popover_powermenu").popup()


def _network_button_event(widget):
    loginwindow.builder.get_object("ui_popover_network").popup()


def _poweroff_event(widget):
    loginwindow.main_stack.set_visible_child_name("page_poweroff")


def _restart_event(widget):
    loginwindow.main_stack.set_visible_child_name("page_restart")


def _cancel_event(widget):
    lightdm.reset_process = False
    lightdm.cancel()
    loginwindow.builder.get_object("ui_entry_reset_username").set_text("")
    loginwindow.main_stack.set_visible_child_name("page_main")


def module_init():
    loginwindow.builder.get_object(
        "ui_button_options").connect("clicked", _options_event)
    loginwindow.builder.get_object(
        "ui_button_powermenu").connect("clicked", _powermenu_event)
    loginwindow.builder.get_object(
        "ui_button_poweroff").connect("clicked", _poweroff_event)
    loginwindow.builder.get_object(
        "ui_button_restart").connect("clicked", _restart_event)
    loginwindow.builder.get_object(
        "ui_button_stack_restart_cancel").connect("clicked", _cancel_event)
    loginwindow.builder.get_object(
        "ui_button_reset_cancel").connect("clicked", _cancel_event)
    loginwindow.builder.get_object(
        "ui_button_stack_poweroff_cancel").connect("clicked", _cancel_event)
    loginwindow.builder.get_object(
        "ui_button_stack_restart").connect("clicked",lightdm.reboot)
    loginwindow.builder.get_object(
        "ui_button_stack_poweroff").connect("clicked",lightdm.shutdown)
