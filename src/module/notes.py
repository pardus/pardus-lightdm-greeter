def _notes_button_event(widget):
    loginwindow.o("ui_popover_notes").popup()


def _save_note_text(buffer):
    text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
    gsettings_set("note-text",text)

def module_init():
    if not get("notes", True):
        loginwindow.o("ui_button_note").hide()
        return
    notes_button = loginwindow.o("ui_button_note")
    loginwindow.o("ui_textview_notes").get_buffer().set_text(gsettings_get("note-text"))
    loginwindow.o("ui_textview_notes").get_buffer().connect("changed", _save_note_text)
    notes_button.connect("clicked", _notes_button_event)
    height = int(monitor.get_common_resolution().split("x")[1])
    width = int(monitor.get_common_resolution().split("x")[0])
    loginwindow.o("ui_popover_notes").set_size_request(width/3, height/3)
    
