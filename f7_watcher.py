#!/usr/bin/env python3
import subprocess
from pathlib import Path
from pynput import keyboard, mouse

SAVE_DIR = Path("/media/cade/F/screenshots")


def get_latest_screenshot():
    latest = max(SAVE_DIR.glob("Screenshot from *.png"),
                 key=lambda f: f.stat().st_mtime, default=None)
    return str(latest) if latest else None


def send_to_claude(path):
    msg = f"Look at the latest screenshot: {path}"
    result = subprocess.run(['xdotool', 'search', '--name', 'Claude'],
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
    stage = ['click']
    done = [False]

    def on_click(x, y, button, pressed):
        if not pressed or done[0]:
            return
        if button == mouse.Button.left and stage[0] == 'click':
            stage[0] = 'f7'
        else:
            done[0] = True
            return False

    def on_key(key):
        if done[0]:
            return False
        if stage[0] == 'f7' and key == keyboard.Key.f7:
            path = get_latest_screenshot()
            if path:
                send_to_claude(path)
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
