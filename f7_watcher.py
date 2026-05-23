#!/usr/bin/env python3
import subprocess
from pathlib import Path
from pynput import keyboard, mouse
from datetime import datetime

SAVE_DIR = Path("/media/cade/ImmutableDrive/screenshots")
LOG = Path("/tmp/f7_watcher.log")

def log(msg):
    with open(LOG, "a") as f:
        f.write(f"{datetime.now().strftime('%H:%M:%S')} {msg}\n")


def get_latest_screenshot():
    latest = max(SAVE_DIR.glob("Screenshot from *.png"),
                 key=lambda f: f.stat().st_mtime, default=None)
    return str(latest) if latest else None


def send_to_claude(path):
    msg = f"Look at the latest screenshot: {path}"
    result = subprocess.run(['xdotool', 'search', '--name', 'Antigravity -'],
                            capture_output=True, text=True)
    windows = [w for w in result.stdout.strip().split('\n') if w]
    if windows:
        wid = windows[0]
        subprocess.run(['xdotool', 'windowfocus', wid])
        subprocess.run(['xdotool', 'type', '--window', wid, '--clearmodifiers', msg])
        subprocess.run(['xdotool', 'key', '--window', wid, 'Return'])
    else:
        subprocess.run(['xdotool', 'type', '--clearmodifiers', msg])
        subprocess.run(['xdotool', 'key', 'Return'])


def main():
    log("f7_watcher started")
    stage = ['click']
    done = [False]

    def on_click(x, y, button, pressed):
        if not pressed or done[0]:
            return
        log(f"click: button={button} stage={stage[0]}")
        if button == mouse.Button.left and stage[0] == 'click':
            stage[0] = 'kp7'
            log("stage -> kp7, waiting for KP_7")
        else:
            log("unexpected click, exiting")
            done[0] = True
            return False

    def on_key(key):
        if done[0]:
            return False
        log(f"key pressed: {key!r} vk={getattr(key, 'vk', None)} char={getattr(key, 'char', None)} stage={stage[0]}")
        if stage[0] == 'kp7' and key == keyboard.KeyCode.from_vk(0xffb7):
            log("KP_7 matched — sending screenshot")
            path = get_latest_screenshot()
            if path:
                send_to_claude(path)
        else:
            log("key did not match KP_7 or wrong stage")
        done[0] = True
        return False

    m = mouse.Listener(on_click=on_click)
    k = keyboard.Listener(on_press=on_key)
    m.start()
    k.start()
    k.join()
    m.stop()


if __name__ == '__main__':
    main()
