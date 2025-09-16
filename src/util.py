#!/usr/bin/python3
import struct
import fcntl
import socket
import configparser
import sys
import os
import time
import threading

from gi.repository import Gio


def asynchronous(func):
    def wrapper(*args, **kwargs):
        debug("async call: "+func.__name__+str(args))
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper


cached_result = {}


def cached(func):
    def wrapper(*args, **kwargs):
        global cached_result
        if func.__name__ in cached_result:
            return cached_result[func.__name__]
        cached_result[func.__name__] = func(*args, **kwargs)
        return cached_result[func.__name__]
    return wrapper


try:
    cfgs = ["/etc/pardus/greeter.conf"]
    if os.path.isdir("/etc/pardus/greeter.conf.d"):
        for cdir in sorted(os.listdir("/etc/pardus/greeter.conf.d/")):
            cfgs.append("/etc/pardus/greeter.conf.d/"+cdir)

    config = configparser.RawConfigParser()
    config.read(cfgs)
except:
    config = []

try:
    kernel_args = {}
    with open("/proc/cmdline", "r") as f:
        cmdline = f.read().split(" ")
        for c in cmdline:
            if "=" in c and c.startswith("lightdm."):
                var = c.split("=")[0]
                val = c[len(var):]
                kernel_args[var] = val
except:
    kernel_args = {}


def get(variable, default=None, section="pardus"):
    if "lightdm.{}.{}".format(section, variable) in kernel_args:
        return kernel_args["lightdm.{}.{}".format(section, variable)]
    if section not in config:
        return default
    if variable not in config[section]:
        return default
    ret = config[section][variable]
    if default in [True, False]:
        return str(ret).lower() == "true"
    return str(ret)


if get("debug", False, "pardus"):
    def debug(msg):
        log("[DEBUG:{}] => {}\n".format(time.time(), msg), type="debug")
else:
    def debug(msg):
        return


gsettings = Gio.Settings.new("tr.org.pardus.lightdm.greeter")


def gsettings_get(variable):
    debug(variable)
    debug(gsettings.get_string(variable))
    return gsettings.get_string(variable)


def gsettings_set(variable, value):
    debug(variable)
    debug(value)
    gsettings.set_string(variable, value)
    gsettings.sync()


def log(msg, type="log"):
    if len(msg.strip()) == 0:
        return
    sys.stderr.write(msg.strip()+"\n")


def readfile(path):
    path = "{}/{}".format(os.environ["HOME"], path)
    path = path.replace("..", "./")
    if not os.path.isfile(path):
        return ""
    f = open(path, "r")
    data = f.read()
    f.close()
    return data.strip()


def writefile(path, data):
    path = "{}/{}".format(os.environ["HOME"], path)
    path = path.replace("..", "./")
    with open(path, "w") as f:
        f.write(data.strip())


def get_ip():
    try:
        import requests
    except Exception:
        return '0.0.0.0'
    # Check internet connection from server list
    servers = open(
        "/usr/share/pardus/pardus-lightdm-greeter/data/servers.txt", "r").read().split("\n")
    debug(servers)
    for server in servers:
        try:
            debug("Server request: "+server)
            r = requests.get(server, timeout=1)
            if r.content:
                return r.content.decode("utf-8")
        except:
            continue
    return '0.0.0.0'


@cached
def is_virtual_machine():
    cpuinfo = readfile("/proc/cpuinfo").split("\n")
    for line in cpuinfo:
        if line.startswith("flags"):
            return "hypervisor" in line
    return False


@cached
def is_virtualbox():
    if os.path.isfile("/sys/class/dmi/id/product_name"):
        with open("/sys/class/dmi/id/product_name", "r") as f:
            if "virtualbox" in f.read().lower():
                return True
            elif "virtual box" in f.read().lower():
                return True
    return False


@cached
def is_debian_based():
    return os.path.exists("/var/lib/dpkg/status")

# https://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-from-a-nic-network-interface-controller-in-python


def get_local_ip():
    ret = []
    for ifname in os.listdir("/sys/class/net"):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15].encode("utf-8"))
            )[20:24])
            if ifname != "lo":
                ret.append((ip, ifname))
        except:
            pass
    return ret


def which(cmd):
    for dir in os.environ["PATH"].split(":"):
        if os.path.exists("{}/{}".format(dir, cmd)):
            return "{}/{}".format(dir, cmd)
    return None
