import json
@asynchronous
def module_init():
    if not get("enabled",True,"daemon"):
        return
    busdir = "/var/lib/lightdm/"
    while True:
        if os.path.exists("/{}/pardus-greeter".format(busdir)):
            os.unlink("/{}/pardus-greeter".format(busdir))
        os.mkfifo("/{}/pardus-greeter".format(busdir))
        f = open("/{}/pardus-greeter".format(busdir),"r")
        username=""
        password=""
        data=json.loads(f.read())
        if "username" in data:
            username=data["username"]
        if "password" in data:
            password = data["password"]
        if "session" in data:
            lightdm.set(session = data["session"])
        loginwindow.o("ui_entry_username").set_text(username)
        loginwindow.o("ui_entry_password").set_text(password)
        lightdm.set(username, password)
        lightdm.login()

