#!/usr/bin/env python3
import sys
import re
import json
import socket
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext

SOCKET_PATH   = "/tmp/browser_daemon.sock"
REMINDER_FILE = Path("/tmp/reminder.txt")
HISTORY_MAX   = 20
WINDOW_CAP    = 100

BG     = "#1a1a1a"
FG     = "#e0e0e0"
BTN_BG = "#2d2d2d"
FONT   = ("Courier", 14)


def get_screen_geometry(screen_num):
    try:
        out = subprocess.check_output(["xrandr", "--query"], text=True)
        monitors = []
        for line in out.splitlines():
            if " connected" in line:
                m = re.search(r'(\d+)x(\d+)\+(\d+)\+(\d+)', line)
                if m:
                    monitors.append((int(m.group(3)), int(m.group(4)),
                                     int(m.group(1)), int(m.group(2))))
        monitors.sort(key=lambda m: m[0])
        if monitors and 1 <= screen_num <= len(monitors):
            x, y, w, h = monitors[screen_num - 1]
            return f"{w}x{h}+{x}+{y}"
    except Exception:
        pass
    return None


class BrowserWindow:
    def __init__(self, root, screen_num, browser_id, file_path, daemon):
        self.browser_id      = browser_id
        self.file_path       = Path(file_path) if file_path else None
        self.daemon          = daemon
        self.reminder_active = False
        self._last_mtime     = None

        self.win = tk.Toplevel(root)
        self.win.title(str(self.file_path) if self.file_path else f"Browser {browser_id}")
        self.win.configure(bg=BG)

        geo = get_screen_geometry(screen_num)
        if geo:
            self.win.geometry(geo)

        bar = tk.Frame(self.win, bg=BTN_BG, pady=3)
        bar.pack(side=tk.TOP, fill=tk.X)
        for label, cmd in [("Copy All", self._copy_all),
                            ("Clear All", self._clear_all),
                            ("Read", self._read_aloud)]:
            tk.Button(bar, text=label, command=cmd,
                      bg=BTN_BG, fg=FG, relief=tk.FLAT,
                      padx=8, pady=2).pack(side=tk.LEFT, padx=2)

        self.text = scrolledtext.ScrolledText(
            self.win, bg=BG, fg=FG, font=FONT,
            insertbackground=FG, wrap=tk.WORD,
            relief=tk.FLAT, padx=24, pady=24
        )
        self.text.pack(fill=tk.BOTH, expand=True)

        self._load()
        self._poll()
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

    def _load(self):
        if self.file_path and self.file_path.exists():
            try:
                content = self.file_path.read_text(encoding="utf-8")
                self._set_text(content)
                self._last_mtime = self.file_path.stat().st_mtime
            except Exception as e:
                self._set_text(f"Error loading file: {e}")
        else:
            self._set_text("")

    def _set_text(self, text):
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, text)

    def _get_text(self):
        return self.text.get("1.0", tk.END).rstrip()

    def _copy_all(self):
        self.win.clipboard_clear()
        self.win.clipboard_append(self._get_text())

    def _clear_all(self):
        self._set_text("")

    def _read_aloud(self):
        text = self._get_text()
        if text:
            proc = subprocess.Popen(["espeak-ng", "-s", "150"], stdin=subprocess.PIPE)
            proc.stdin.write(text.encode())
            proc.stdin.close()

    def _poll(self):
        reminder_exists = REMINDER_FILE.exists()
        if reminder_exists and not self.reminder_active:
            try:
                msg = REMINDER_FILE.read_text().strip() or "Time to move!"
            except Exception:
                msg = "Time to move!"
            self._set_text(f"†\n\n{msg}")
            self.reminder_active = True
        elif not reminder_exists and self.reminder_active:
            self.reminder_active = False
            self._load()
        elif not self.reminder_active and self.file_path and self.file_path.exists():
            try:
                mtime = self.file_path.stat().st_mtime
                if self._last_mtime is not None and mtime != self._last_mtime:
                    self._save_history()
                    self._load()
            except Exception:
                pass
        self.win.after(500, self._poll)

    def _save_history(self):
        history_dir = Path("/media/cade/ImmutableDrive/file-history")
        if history_dir.exists() and self.file_path:
            try:
                ts    = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                dest  = history_dir / f"{self.file_path.stem}_{ts}{self.file_path.suffix}"
                dest.write_bytes(self.file_path.read_bytes())
                copies = sorted(history_dir.glob(
                    f"{self.file_path.stem}_*{self.file_path.suffix}"))
                for old in copies[:-HISTORY_MAX]:
                    old.unlink(missing_ok=True)
            except Exception:
                pass

    def _on_close(self):
        self.daemon.active_windows.pop(self.browser_id, None)
        self.win.destroy()


class BrowserDaemon:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.active_windows = {}
        self._next_id = 1
        self._start_socket_server()

    def _start_socket_server(self):
        Path(SOCKET_PATH).unlink(missing_ok=True)

        def serve():
            srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            srv.bind(SOCKET_PATH)
            srv.listen(5)
            while True:
                try:
                    conn, _ = srv.accept()
                    data = conn.recv(4096).decode()
                    msg  = json.loads(data)
                    self.root.after(0, lambda m=msg: self.open_window(
                        m.get("screen", 2), m.get("file")))
                    conn.send(b'{"ok":true}')
                    conn.close()
                except Exception:
                    pass

        threading.Thread(target=serve, daemon=True).start()

    def open_window(self, screen_num, file_path=None):
        if len(self.active_windows) >= WINDOW_CAP:
            return
        bid = self._next_id
        self._next_id += 1
        win = BrowserWindow(self.root, screen_num, bid, file_path, self)
        self.active_windows[bid] = win

    def run(self):
        self.root.mainloop()


def try_send_to_daemon(screen, file_path):
    for attempt in range(3):
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect(SOCKET_PATH)
            sock.sendall(json.dumps({"screen": screen, "file": file_path}).encode())
            sock.close()
            return True
        except (OSError, socket.error):
            if attempt < 2:
                time.sleep(0.1)
    return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Personal browser")
    parser.add_argument("screen", type=int)
    parser.add_argument("file",   nargs="?", default=None)
    args = parser.parse_args()

    if try_send_to_daemon(args.screen, args.file):
        sys.exit(0)

    daemon = BrowserDaemon()
    daemon.open_window(args.screen, args.file)
    daemon.run()
