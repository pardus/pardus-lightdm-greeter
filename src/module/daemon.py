import json
@asynchronous
def module_init():
    if os.path.exists("/{}/pardus-greeter".format(busdir)):
        os.unlink("/{}/pardus-greeter".format(busdir))
    if not get("enabled",True,"daemon"):
        return
    busdir = "/var/lib/lightdm/"
    while True:
        os.mkfifo("/{}/pardus-greeter".format(busdir))
        try:
            with open("/{}/pardus-greeter".format(busdir),"r") as f:
                username=""
                password=""
                data=json.loads(f.read())
                if "username" in data:
                    username=str(data["username"])
                if "password" in data:
                    password = str(data["password"])
                if "session" in data:
                    lightdm.set(session = str(data["session"]))
                loginwindow.o("ui_entry_username").set_text(username)
                loginwindow.o("ui_entry_password").set_text(password)
                lightdm.set(username, password)
                lightdm.login()
        except Exception as e:
           print(traceback.format_exc(), file=sys.stderr)
        os.unlink("/{}/pardus-greeter".format(busdir))
