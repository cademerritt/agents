#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path
import evdev

FLAG = Path("/tmp/mic_active")
DEVICE_PATH = "/dev/input/event7"


def focus_claude():
    result = subprocess.run(["xdotool", "search", "--class", "Code"],
                            capture_output=True, text=True)
    windows = [w for w in result.stdout.strip().splitlines() if w]
    if windows:
        wid = windows[-1]
        subprocess.run(["xdotool", "windowactivate", "--sync", wid])
        time.sleep(0.15)
        subprocess.run(["xdotool", "key", "--clearmodifiers", "ctrl+Escape"])
        time.sleep(0.15)


def send_key(key):
    subprocess.run(["xdotool", "key", "--clearmodifiers", key])


def main():
    dev = evdev.InputDevice(DEVICE_PATH)
    for event in dev.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            key = evdev.categorize(event)
            if key.keycode == "BTN_EXTRA" and key.keystate == 1:
                if FLAG.exists():
                    FLAG.unlink()
                    send_key("ctrl+d")
                    send_key("Return")
                else:
                    FLAG.touch()
                    focus_claude()
                    send_key("ctrl+d")


if __name__ == "__main__":
    main()
