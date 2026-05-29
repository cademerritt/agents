#!/usr/bin/env python3
import threading
import tkinter as tk
import evdev
import keyboard
import subprocess
import time

DEVICE = "/dev/input/by-id/usb-Compx_2.4G_Receiver-if01-event-mouse"
FORWARD_BUTTON = evdev.ecodes.BTN_EXTRA

def cursor_is_focused():
    result = subprocess.run(
        ["xdotool", "getactivewindow", "getwindowname"],
        capture_output=True, text=True
    )
    return "Cursor" in result.stdout

device = evdev.InputDevice(DEVICE)

while True:  # focus is on the text/message window
    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY and event.code == FORWARD_BUTTON and event.value == 1:
            for i in range(2):
                subprocess.run(["wmctrl", "-a", "cade"])
                time.sleep(0.5)
                keyboard.send('ctrl+d')
            for event2 in device.read_loop():
                if event2.type == evdev.ecodes.EV_KEY and event2.code == FORWARD_BUTTON and event2.value == 1:
                    if not cursor_is_focused():
                        break
                    keyboard.send('Return')
                    for event3 in device.read_loop():
                        if event3.type == evdev.ecodes.EV_KEY and event3.code == FORWARD_BUTTON and event3.value == 1:
                            if not cursor_is_focused():
                                break
                            keyboard.send('ctrl+d')
                            break


# --- DESIGN PLAN (next session) ---
# Wrap the event loop in: while True:
#
# STAGE 1 — Cursor not focused:
#   Button press → focus Cursor message box + ctrl+d (mic on) → break inner loop
#   while True restarts the event loop from the top.
#
# STAGE 2 — Cursor IS focused (sub-loop, no break):
#   mic off → button press → ctrl+d (mic on)
#   mic on  → button press → Enter (sends message, mic off automatically)
#   Repeats: mic on, Enter, mic on, Enter — as long as focus stays.
#
# Focus check happens on EVERY button press (not a continuous poll).
# If focus is gone at press time → Stage 1.
# One if at the top of the handler. No need for multiple if-false checks.
