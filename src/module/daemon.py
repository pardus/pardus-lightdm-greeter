import json
@asynchronous
def module_init():
    busdir = "/var/lib/lightdm/"
    if os.path.exists("/{}/pardus-greeter".format(busdir)):
        os.unlink("/{}/pardus-greeter".format(busdir))
    if not get("enabled",True,"daemon"):
        return
    while True:
        debug("Creating fifo")
        os.mkfifo("/{}/pardus-greeter".format(busdir))
        try:
            with open("/{}/pardus-greeter".format(busdir),"r") as f:
                username=""
                password=""
                debug("Reading fifo")
                data=json.loads(f.read())
                debug("fifo data: {}".format(str(data)))
                os.unlink("/{}/pardus-greeter".format(busdir))
                debug("Removing fifo")
                if "username" in data:
                    username=str(data["username"])
                if "password" in data:
                    password = str(data["password"])
                if "session" in data:
                    lightdm.set(session = str(data["session"]))
                GLib.idle_add(loginwindow.o("ui_entry_username").set_text, username)
                GLib.idle_add(loginwindow.o("ui_entry_password").set_text, password)
                lightdm.set(username, password)
                lightdm.login()
        except Exception as e:
           if os.path.exists("/{}/pardus-greeter".format(busdir)):
               os.unlink("/{}/pardus-greeter".format(busdir))
               debug("Removing fifo")
           print(traceback.format_exc(), file=sys.stderr)
