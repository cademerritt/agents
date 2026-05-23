#!/usr/bin/env python3
import subprocess
from pathlib import Path

FLAG = Path("/tmp/mic_active")


def get_vscode_wid():
    result = subprocess.run(['xdotool', 'search', '--class', 'Code'],
                            capture_output=True, text=True)
    windows = [w for w in result.stdout.strip().split('\n') if w]
    return windows[0] if windows else None


def main():
    wid = get_vscode_wid()

    if FLAG.exists():
        FLAG.unlink()
        if wid:
            subprocess.run(['xdotool', 'windowactivate', '--sync', wid])
            subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+d'])
            subprocess.run(['xdotool', 'key', '--clearmodifiers', 'Return'])
        else:
            subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+d'])
            subprocess.run(['xdotool', 'key', '--clearmodifiers', 'Return'])
    else:
        FLAG.touch()
        if wid:
            subprocess.run(['xdotool', 'windowactivate', '--sync', wid])
            subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+d'])
        else:
            subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+d'])


if __name__ == '__main__':
    main()
