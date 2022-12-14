def which(cmd):
    for dir in os.environ["PATH"].split(":"):
        if os.path.exists("{}/{}".format(dir, cmd)):
            return "{}/{}".format(dir, cmd)
    return None


def module_init():
    for wm in ["xfwm4", "metacity", "openbox", "mate-wm", "mutter"]:
        if which(wm.split(" ")[0]):
            subprocess.run(["{} 2>/dev/null &".format(wm)], shell=True)
        break
