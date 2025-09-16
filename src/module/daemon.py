import json

############### Main thread functions ###############

def process_daemon_data(data):
    ### message and event
    if "message" in data:
        lightdm.msg_handler(str(data["message"]))
    if "event" in data:
        if data["event"] == "block-gui":
            loginwindow.block_gui()
        elif data["event"] == "unblock-gui":
            loginwindow.unblock_gui()
    if "message" in data or "event" in data:
        return
    ### login
    username = ""
    password = ""
    if "username" in data:
        username = str(data["username"])
    if "password" in data:
        password = str(data["password"])
    if "session" in data:
        lightdm.set(session=str(data["session"]))
    loginwindow.o("ui_entry_username").set_text(username)
    loginwindow.o("ui_entry_password").set_text(password)
    loginwindow.event_login_button(loginwindow.o("ui_button_login"))
    debug("daemon login done")


def daemon_func():
    busdir = "/var/lib/lightdm/"
    if os.path.exists("/{}/pardus-greeter".format(busdir)):
        os.unlink("/{}/pardus-greeter".format(busdir))
    debug("Entering daemon loop")
    while True:
        time.sleep(1) # wait 1 second
        debug("Creating fifo")
        os.mkfifo("/{}/pardus-greeter".format(busdir))
        try:
            debug("Listening fifo")
            with open("/{}/pardus-greeter".format(busdir), "r") as f:
                debug("Reading fifo")
                data = f.read()
                data = json.loads(data)
                debug("fifo data: {}".format(str(data)))
                os.unlink("/{}/pardus-greeter".format(busdir))
                debug("Removing fifo after read")
                GLib.idle_add(process_daemon_data, data)
        except Exception as e:
            debug("Removing fifo")
            if os.path.exists("/{}/pardus-greeter".format(busdir)):
                os.unlink("/{}/pardus-greeter".format(busdir))
                debug("Removing fifo done")
            print(e, traceback.format_exc(), file=sys.stderr)

############### Async functions ###############

def module_init():
    if not get("enabled", True, "daemon"):
        return
    dm = threading.Thread(target=daemon_func)
    dm.start()
