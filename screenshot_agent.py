#!/usr/bin/env python3
import logging
import os
import re
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from datetime import datetime
from pynput import mouse

SAVE_DIR    = Path("/home/cade/screenshots")
ANIM_SCRIPT = Path(__file__).parent / "screenshot_anim.py"
SOCK_PATH   = "/tmp/screenshot_agent.sock"
LOG_PATH    = Path(__file__).parent / "logs/screenshot_agent.log"

IDLE            = 0
WAITING_CLICK   = 1
WAITING_CONFIRM = 2

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger("screenshot_agent")


class ScreenshotAgent:
    def __init__(self):
        self.state       = IDLE
        self.latest_path = None
        self.anim_proc   = None
        self.lock        = threading.Lock()
        log.info("ScreenshotAgent started")

    def get_monitor_for_point(self, x, y):
        try:
            result = subprocess.run(["xrandr"], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines():
                if "connected" in line and "disconnected" not in line:
                    m = re.search(r"(\d+)x(\d+)\+(\d+)\+(\d+)", line)
                    if m:
                        w, h, ox, oy = map(int, m.groups())
                        if ox <= x < ox + w and oy <= y < oy + h:
                            return ox, oy, w, h
        except Exception:
            log.exception("get_monitor_for_point failed")
        return None

    def take_screenshot(self, x, y):
        try:
            SAVE_DIR.mkdir(parents=True, exist_ok=True)
            ts   = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            path = SAVE_DIR / f"Screenshot from {ts}.png"
            geo  = self.get_monitor_for_point(x, y)
            if geo:
                ox, oy, w, h = geo
                cmd = ["scrot", "-a", f"{ox},{oy},{w},{h}", str(path)]
            else:
                cmd = ["scrot", str(path)]
            res = subprocess.run(cmd, capture_output=True, check=False)
            if res.returncode == 0 and path.exists():
                log.info("Screenshot saved: %s", path)
                return str(path)
            else:
                log.error("scrot failed (rc=%d): %s", res.returncode, res.stderr.decode())
        except Exception:
            log.exception("take_screenshot failed")
        return None

    def start_animation(self):
        self.stop_animation()
        try:
            self.anim_proc = subprocess.Popen(
                [sys.executable, str(ANIM_SCRIPT)],
                env=os.environ.copy(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            log.exception("start_animation failed")
            self.anim_proc = None

    def stop_animation(self):
        if self.anim_proc and self.anim_proc.poll() is None:
            try:
                self.anim_proc.terminate()
                self.anim_proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                try:
                    self.anim_proc.kill()
                except Exception:
                    log.exception("stop_animation kill failed")
        self.anim_proc = None

    def reset(self):
        self.state = IDLE
        self.stop_animation()

    def focus_claude(self):
        try:
            result = subprocess.run(["xdotool", "search", "--class", "Code"],
                                    capture_output=True, text=True, check=False)
            windows = [w for w in result.stdout.strip().splitlines() if w]
            if windows:
                wid = windows[-1]
                subprocess.run(["xdotool", "windowactivate", "--sync", wid], check=False)
                time.sleep(0.15)
        except Exception:
            log.exception("focus_claude failed")

    def send_to_claude(self, path):
        msg = f"t the latest screenshot: {path}"
        try:
            self.focus_claude()
            subprocess.run(["xdotool", "type", "--clearmodifiers", "--delay", "0", msg], check=False)
            subprocess.run(["xdotool", "key", "Return"], check=False)
            log.info("Sent to Claude: %s", path)
        except Exception:
            log.exception("send_to_claude failed")

    def paste_to_gemini(self, path):
        try:
            if not os.path.exists(path):
                log.warning("paste_to_gemini: path not found: %s", path)
                return
            with open(path, "rb") as f:
                subprocess.run(["xclip", "-selection", "clipboard", "-t", "image/png"],
                               stdin=f, check=False)
            for name in ["Gemini", "Google DeepMind", "ChatGPT"]:
                result = subprocess.run(["xdotool", "search", "--name", name],
                                        capture_output=True, text=True, check=False)
                windows = [w for w in result.stdout.strip().splitlines() if w]
                if windows:
                    wid = windows[0]
                    subprocess.run(["xdotool", "windowfocus", wid], check=False)
                    subprocess.run(["xdotool", "key", "--window", wid, "ctrl+v"], check=False)
                    log.info("Pasted to %s", name)
                    return
            subprocess.run(["xdotool", "key", "ctrl+v"], check=False)
        except Exception:
            log.exception("paste_to_gemini failed")

    def handle_kp8(self):
        with self.lock:
            if self.state == IDLE:
                self.start_animation()
                self.state = WAITING_CLICK
            else:
                self.reset()

    def handle_kp7(self):
        path_to_send = None
        with self.lock:
            if self.state == WAITING_CONFIRM and self.latest_path:
                path_to_send = self.latest_path
            self.reset()
        if path_to_send:
            self.send_to_claude(path_to_send)

    def handle_kp9(self):
        path_to_paste = None
        with self.lock:
            if self.state == WAITING_CONFIRM and self.latest_path:
                path_to_paste = self.latest_path
            self.reset()
        if path_to_paste:
            self.paste_to_gemini(path_to_paste)

    def on_click(self, x, y, button, pressed):
        if not pressed:
            return
        with self.lock:
            if self.state == WAITING_CLICK and button == mouse.Button.left:
                self.stop_animation()
                path = self.take_screenshot(x, y)
                if path:
                    self.latest_path = path
                    self.state = WAITING_CONFIRM
                else:
                    log.error("Screenshot failed — resetting state")
                    self.reset()
            elif self.state != IDLE:
                self.reset()

    def run_socket_server(self):
        if os.path.exists(SOCK_PATH):
            try:
                os.unlink(SOCK_PATH)
            except Exception:
                log.exception("Could not unlink socket")
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(SOCK_PATH)
        server.listen(5)
        log.info("Socket server listening at %s", SOCK_PATH)
        while True:
            try:
                conn, _ = server.accept()
                with conn:
                    cmd = conn.recv(16).decode("utf-8").strip()
                if cmd == "kp8":
                    self.handle_kp8()
                elif cmd == "kp7":
                    self.handle_kp7()
                elif cmd == "kp9":
                    self.handle_kp9()
                else:
                    log.warning("Unknown command: %s", cmd)
            except Exception:
                log.exception("Socket server error")

    def run(self):
        t = threading.Thread(target=self.run_socket_server, daemon=True)
        t.start()
        with mouse.Listener(on_click=self.on_click) as m_listener:
            m_listener.join()


if __name__ == "__main__":
    agent = ScreenshotAgent()
    agent.run()
