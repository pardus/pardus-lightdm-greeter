#!/bin/bash
exe=""
if which dbus-run-session &>/dev/null; then
    exe="dbus-run-session"
fi
exec $exe python3 /usr/share/pardus/pardus-lightdm-greeter/main.py 1>&2
