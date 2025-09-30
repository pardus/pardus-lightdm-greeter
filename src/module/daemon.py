import socket
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
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind("/{}/pardus-greeter".format(busdir))
    server.listen(1)

    debug("Entering daemon loop")
    while True:
        connection, client_address = server.accept()
        try:
            data = connection.recv(1024**2) # read max 1mb
            data = json.loads(data.decode())
            debug("socket data: {}".format(str(data)))
            GLib.idle_add(process_daemon_data, data)
        except Exception as e:
            print(e, traceback.format_exc(), file=sys.stderr)

############### Async functions ###############

def module_init():
    if not get("enabled", True, "daemon"):
        return
    dm = threading.Thread(target=daemon_func)
    dm.start()
