#!/usr/bin/env python3
import subprocess
import time

BINDING_SCREENSHOT = 'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/'
BINDING_MIC        = 'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom1/'
BINDING_SEND       = 'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom2/'


def is_antigravity_running():
    result = subprocess.run(['pgrep', '-f', '/usr/share/antigravity/antigravity'],
                            capture_output=True)
    return result.returncode == 0


def enable_hotkeys():
    subprocess.run(['gsettings', 'set', BINDING_SCREENSHOT, 'binding', 'KP_8'], capture_output=True)
    subprocess.run(['gsettings', 'set', BINDING_MIC,        'binding', 'KP_6'], capture_output=True)
    subprocess.run(['gsettings', 'set', BINDING_SEND,       'binding', 'KP_7'], capture_output=True)
    print("Hotkeys ON")


def disable_hotkeys():
    subprocess.run(['gsettings', 'set', BINDING_SCREENSHOT, 'binding', ''], capture_output=True)
    subprocess.run(['gsettings', 'set', BINDING_MIC,        'binding', ''], capture_output=True)
    subprocess.run(['gsettings', 'set', BINDING_SEND,       'binding', ''], capture_output=True)
    print("Hotkeys OFF")


def main():
    was_running = None
    while True:
        is_running = is_antigravity_running()
        if is_running and not was_running:
            enable_hotkeys()
        elif not is_running and was_running:
            disable_hotkeys()
        was_running = is_running
        time.sleep(2)


if __name__ == '__main__':
    main()
