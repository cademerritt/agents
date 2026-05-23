#!/usr/bin/env python3
import subprocess
from pathlib import Path

SAVE_DIR = Path("/media/cade/ImmutableDrive/screenshots")


def get_latest_screenshot():
    latest = max(SAVE_DIR.glob("Screenshot from *.png"),
                 key=lambda f: f.stat().st_mtime, default=None)
    return str(latest) if latest else None


def main():
    path = get_latest_screenshot()
    if not path:
        return
    msg = f"t the latest screenshot: {path}"
    result = subprocess.run(['xdotool', 'search', '--name', 'VSCode -'],
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


if __name__ == '__main__':
    main()
