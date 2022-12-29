def _options_event(widget):
    loginwindow.o("ui_revealer_default_session").set_reveal_child(False)
    loginwindow.o("ui_revealer_keyboard_layout").set_reveal_child(False)
    loginwindow.o("ui_icon_default_session_dd").set_from_icon_name("go-next-symbolic", 0)
    loginwindow.o("ui_icon_keyboard_layout_dd").set_from_icon_name("go-next-symbolic", 0)
    loginwindow.o("ui_popover_options").popup()

def _powermenu_event(widget):
    loginwindow.o("ui_popover_powermenu").popup()


def _network_button_event(widget):
    loginwindow.o("ui_popover_network").popup()


def _poweroff_event(widget):
    loginwindow.o("ui_stack_main").set_visible_child_name("page_poweroff")


def _restart_event(widget):
    loginwindow.o("ui_stack_main").set_visible_child_name("page_restart")


def _cancel_event(widget):
    loginwindow.err_handler()
    loginwindow.msg_handler("")
    loginwindow.o("ui_entry_reset_username").set_text("")
    loginwindow.o("ui_stack_main").set_visible_child_name("page_main")


def module_init():
    loginwindow.o("ui_button_options").connect("clicked", _options_event)
    loginwindow.o("ui_button_powermenu").connect("clicked", _powermenu_event)
    loginwindow.o("ui_button_poweroff").connect("clicked", _poweroff_event)
    loginwindow.o("ui_button_restart").connect("clicked", _restart_event)
    loginwindow.o("ui_button_stack_restart_cancel").connect("clicked", _cancel_event)
    loginwindow.o("ui_button_reset_cancel").connect("clicked", _cancel_event)
    loginwindow.o("ui_button_stack_poweroff_cancel").connect("clicked", _cancel_event)
    loginwindow.o("ui_button_stack_restart").connect("clicked",lightdm.reboot)
    loginwindow.o("ui_button_stack_poweroff").connect("clicked",lightdm.shutdown)
