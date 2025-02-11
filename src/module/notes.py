def _notes_button_event(widget):
    loginwindow.o("ui_popover_notes").popup()


def _save_note_text(buffer):
    text = buffer.get_text(buffer.get_start_iter(),
                           buffer.get_end_iter(), False)
    gsettings_set("note-text", text)


def module_init():
    if not get("enabled", True, "notes"):
        loginwindow.o("ui_button_note").hide()
        return
    notes_button = loginwindow.o("ui_button_note")
    notes_button.connect("clicked", _notes_button_event)
    height = int(monitor.get_common_resolution().split("x")[1])
    width = int(monitor.get_common_resolution().split("x")[0])
    loginwindow.o("ui_popover_notes").set_size_request(width/3, height/3)
    if get("text-file", "", "notes") != "":
        with open(get("text-file", "", "notes"), "r") as f:
            content = f.read().strip()
            if len(content) > 0:
                loginwindow.o(
                    "ui_textview_notes").get_buffer().set_text(content)
            else:
                loginwindow.o("ui_button_note").hide()
                return
        loginwindow.o("ui_textview_notes").set_editable(False)
        loginwindow.o("ui_textview_notes").set_can_focus(False)
        return
    content = gsettings_get("note-text").strip()
    editable = get("editable", True, "notes")
    if not editable and len(content) == 0:
        loginwindow.o("ui_button_note").hide()
        return
    loginwindow.o("ui_textview_notes").get_buffer().set_text(content)
    loginwindow.o("ui_textview_notes").set_can_focus(editable)
    loginwindow.o("ui_textview_notes").set_editable(editable)
    loginwindow.o("ui_textview_notes").get_buffer().connect(
        "changed", _save_note_text)
