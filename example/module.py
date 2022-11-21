# pardus greeter run module_init function
def module_init():
    # Get login container from glabe
    login_box = loginwindow.builder.get_object("ui_box_login")
    # define new label
    label = Gtk.Label("Hello world")
    # add label to login container
    login_box.pack_start(label,false,false,0)