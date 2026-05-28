#!/usr/bin/env python3
import evdev
import threading
import glob

def monitor(path):
    try:
        device = evdev.InputDevice(path)
        print(f"Monitoring: {device.name}")
        for event in device.read_loop():
            if event.type == evdev.ecodes.EV_KEY and event.value == 1:
                key = evdev.ecodes.KEY.get(event.code, event.code)
                print(f"PRESS: {key}")
    except Exception:
        pass

for path in glob.glob("/dev/input/event*"):
    threading.Thread(target=monitor, args=(path,), daemon=True).start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Stopped.")
