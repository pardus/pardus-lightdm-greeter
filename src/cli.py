#!/usr/bin/env python3
"""
Pardus Lightdm Greeter Command Line Interface
Usage:
    pardus-login <username> <password> <session>
"""
import json
import os
import sys

if os.getuid() != 0:
    print("You must be root!", file=sys.stderr)
    sys.exit(1)


def login(username=None, password=None, session=None):
    """Login function"""
    if not os.path.exists("/var/lib/lightdm/pardus-greeter"):
        print("Failed to connect pardus lightdm greeter")
        sys.exit(2)
    data = {}
    data["username"] = str(username)
    data["password"] = str(password)
    if session:
        data["session"] = str(session)

    with open("/var/lib/lightdm/pardus-greeter", "a") as f:
        print(json.dumps(data))
        f.write(json.dumps(data))
        f.flush()

def send_message(message=None):
    """Print message function"""
    if not os.path.exists("/var/lib/lightdm/pardus-greeter"):
        print("Failed to connect pardus lightdm greeter")
        sys.exit(2)
    data = {}
    data["message"] = str(message)
    with open("/var/lib/lightdm/pardus-greeter", "a") as f:
        print(json.dumps(data))
        f.write(json.dumps(data))
        f.flush()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: pardus-login [username] [password]", file=sys.stderr)
        sys.exit(1)
    if sys.argv[1] == "message":
        send_message(sys.argv[2])
        sys.exit(0)
    session = None
    if len(sys.argv) > 3:
        session = sys.argv[3]
    login(sys.argv[1], sys.argv[2], session)
