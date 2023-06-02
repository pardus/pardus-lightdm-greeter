last_label_clock = None
last_label_date = None
date_format = ""
clock_format = ""


def clock_event():
    global last_label_clock
    global last_label_date
    label_clock = time.strftime(clock_format)
    label_date = time.strftime(date_format)

    if last_label_clock != label_clock:
        last_label_clock = label_clock
        debug("Clock update")
        loginwindow.o("ui_label_time").set_label(
            "<span font='64'>{}</span>".format(label_clock))
    if last_label_date != label_date:
        last_label_date = label_date
        debug("Date update")
        loginwindow.o("ui_label_date").set_label(
            "<span font='16'>{}</span>".format(label_date))
    GLib.timeout_add(1000, clock_event)


def module_init():
    global date_format
    global clock_format
    date_format = get("date-format", "%e %b %Y - %A",
                      "clock").replace("\\n", "\n")
    clock_format = get("clock-format", "%H:%M", "clock").replace("\\n", "\n")
    clock_event()
