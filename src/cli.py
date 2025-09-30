#!/usr/bin/env python3
"""
Pardus Lightdm Greeter Command Line Interface
Usage:
    pardus-login <username> <password> <session>
"""
import json
import os
import sys

import socket

if os.getuid() != 0:
    print("You must be root!", file=sys.stderr)
    sys.exit(1)


def __send_sock(data):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect("/var/lib/lightdm/pardus-greeter")
    client.sendall(data.encode())
    client.close()


def login(username=None, password=None, session=None):
    """Login function"""
    if not os.path.exists("/var/lib/lightdm/pardus-greeter"):
        print("Failed to connect pardus lightdm greeter")
        return 2
    data = {}
    data["username"] = str(username)
    data["password"] = str(password)
    if session:
        data["session"] = str(session)

    __send_sock(json.dumps(data))
    return 0

def send_message(message=None):
    """Print message function"""
    if not os.path.exists("/var/lib/lightdm/pardus-greeter"):
        print("Failed to connect pardus lightdm greeter")
        return 2
    data = {}
    data["message"] = str(message)

    __send_sock(json.dumps(data))
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: pardus-login [username] [password]", file=sys.stderr)
        sys.exit(1)
    if sys.argv[1] == "message":
        sys.exit(send_message(sys.argv[2]))
    session = None
    if len(sys.argv) > 3:
        session = sys.argv[3]
    sys.exit(login(sys.argv[1], sys.argv[2], session))
