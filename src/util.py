#!/usr/bin/python3
import configparser
import sys
import os
import time
import threading
import subprocess


def asynchronous(func):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper




try:
    cfgs = ["/etc/pardus/greeter.conf"]
    if os.path.isdir("/etc/pardus/greeter.conf.d/"):
        for cdir in os.listdir("/etc/pardus/greeter.conf.d/"):
            cfgs.append("/etc/pardus/greeter.conf.d/"+cdir)

    config = configparser.RawConfigParser()
    config.read(cfgs)
except:
    config = []


def get(variable, default=None, section="pardus"):
    if section not in config:
        return default
    if variable not in config[section]:
        return default
    ret = config[section][variable]
    if default == True or default == False:
        if str(ret).lower() == "true":
            return True
        else:
            return False
    return str(ret)

if get("debug", False, "pardus"):
    def debug(msg):
        log("[DEBUG] => {}\n".format(msg), type="debug")
else:
    def debug(msg):
        return


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
    servers = open("/usr/share/pardus/pardus-lightdm-greeter/data/servers.txt","r").read().split("\n")
    debug(servers)
    for server in servers:
        try:
            debug("Server request: "+server)
            r = requests.get(server,timeout=1)
            if r.content:
                return r.content.decode("utf-8")
        except:
            continue
    return '0.0.0.0'

def is_virtual_machine():
    cpuinfo = readfile("/proc/cpuinfo").split("\n")
    for line in cpuinfo:
        if line.startswith("flags"):
            return "hypervisor" in line
    return False

def is_virtualbox():
    if os.path.isfile("/sys/class/dmi/id/product_name"):
        with open("/sys/class/dmi/id/product_name","r") as f:
            if "virtualbox" in f.read().lower():
                return True
            elif "virtual box" in f.read().lower():
                return True
    return False

# https://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-from-a-nic-network-interface-controller-in-python
import socket
import fcntl
import struct
def  get_local_ip():
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
                ret.append((ip,ifname))
        except:
            pass
    return ret
