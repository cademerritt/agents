#!/usr/bin/env python3
# evdev reads directly from the kernel device file — bypasses pynput and X11 limitations.
# Button 9 (BTN_EXTRA) is the forward mouse button.
# device.grab() is NOT called — normal OS mouse behavior is preserved.
# User must be in the input group: sudo usermod -aG input cade (then re-login, one time only).
import subprocess
import evdev
import os

os.environ["XDG_RUNTIME_DIR"] = "/run/user/1000"
os.environ["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/run/user/1000/bus"

DEVICE = "/dev/input/by-id/usb-Compx_2.4G_Receiver-if01-event-mouse"
FORWARD_BUTTON = evdev.ecodes.BTN_EXTRA

def is_muted():
    result = subprocess.run(["wpctl", "get-volume", "33"], capture_output=True, text=True)
    return "MUTED" in result.stdout


def focus_cursor():
    result = subprocess.run(
        ["xdotool", "search", "--class", "Cursor"],
        capture_output=True, text=True
    )
    windows = [w for w in result.stdout.strip().splitlines() if w]
    if windows:
        subprocess.run(["xdotool", "windowactivate", windows[-1]])


def mic_unmute():
    subprocess.run(["wpctl", "set-mute", "33", "0"])


def mic_mute():
    subprocess.run(["wpctl", "set-mute", "33", "1"])


def fire():
    subprocess.run(["xdotool", "key", "Return"])


device = evdev.InputDevice(DEVICE)

for event in device.read_loop():
    if event.type == evdev.ecodes.EV_KEY and event.code == FORWARD_BUTTON and event.value == 1:
        if is_muted():
            focus_cursor()
            mic_unmute()
        else:
            mic_mute()
            fire()
