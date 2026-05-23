#!/usr/bin/env python3
import evdev
import subprocess

def find_device():
    for path in evdev.list_devices():
        dev = evdev.InputDevice(path)
        if "Compx 2.4G Receiver Mouse" in dev.name:
            return dev
    return None

def main():
    dev = find_device()
    if not dev:
        print("Compx mouse not found")
        return
    for event in dev.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            key = evdev.categorize(event)
            if key.keycode == "BTN_EXTRA" and key.keystate == 1:
                subprocess.Popen(["/home/cade/venv/bin/python",
                                  "/home/cade/agents/f6_mic.py"])

if __name__ == "__main__":
    main()
