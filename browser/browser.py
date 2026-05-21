#!/usr/bin/env python3
import sys
import re
import json
import time
import socket
import argparse
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtNetwork import QLocalServer
from PyQt6.QtCore import Qt, QUrl, QFileSystemWatcher, QTimer

SOCKET_PATH   = "/tmp/browser_daemon.sock"
REMINDER_FILE = Path("/tmp/reminder.txt")
WALLPAPER     = Path("/home/cade/.local/share/backgrounds/2026-04-18-17-10-32-Picture1.png")
HISTORY_MAX   = 20
WINDOW_CAP    = 100

DAGGER_HTML = """<!DOCTYPE html>
<html><head><style>
  body {{ background:#1a1a1a; color:#e0e0e0; font-family:monospace;
          display:flex; flex-direction:column; justify-content:center;
          align-items:center; height:100vh; margin:0; }}
  .dagger {{ font-size:140px; color:#ff4444; line-height:1; }}
  .msg {{ font-size:34px; margin-top:24px; text-align:center; }}
</style></head>
<body>
  <div class="dagger">†</div>
  <div class="msg">{msg}</div>
</body></html>"""

CONTENT_TEMPLATE = """<!DOCTYPE html>
<html><head><style>
  body {{ background:#1a1a1a; color:#e0e0e0; font-family:monospace;
          padding:32px; margin:0; line-height:1.7; font-size:15px;
          word-wrap:break-word; overflow-wrap:break-word; }}
  h1, h2, h3 {{ color:#61afef; margin-top:1.4em; }}
  code {{ background:#2d2d2d; padding:2px 6px; border-radius:3px; color:#98c379; }}
  pre {{ background:#2d2d2d; padding:16px; border-radius:6px; overflow-x:auto; margin:12px 0; }}
  pre code {{ background:none; padding:0; color:#abb2bf; }}
  li {{ margin:5px 0; }}
  ul {{ list-style-type: decimal; padding-left:1.5em; }}
  p {{ margin:7px 0; }}
  strong {{ color:#e5c07b; }}
  a {{ color:#61afef; }}
  hr {{ border:none; border-top:1px solid #333; margin:20px 0; }}
</style></head>
<body>{content}</body></html>"""


def md_to_html(text):
    try:
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        def replace_code_block(m):
            lang = m.group(1) or ""
            code = m.group(2)
            return f'<pre><code class="language-{lang}">{code}</code></pre>'
        text = re.sub(r'```(\w*)\n(.*?)```', replace_code_block, text, flags=re.DOTALL)

        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', text, flags=re.MULTILINE)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'^---$', r'<hr>', text, flags=re.MULTILINE)

        text = re.sub(r'^\d+\. (.+)$', r'<OL_ITEM>\1</OL_ITEM>', text, flags=re.MULTILINE)
        text = re.sub(r'(<OL_ITEM>.*?</OL_ITEM>\n{0,2})+',
                      lambda m: '<ol>\n' + m.group(0).replace('<OL_ITEM>', '<li>').replace('</OL_ITEM>', '</li>') + '</ol>\n',
                      text, flags=re.DOTALL)

        text = re.sub(r'^[-*] (.+)$', r'<UL_ITEM>\1</UL_ITEM>', text, flags=re.MULTILINE)
        text = re.sub(r'(<UL_ITEM>.*?</UL_ITEM>\n{0,2})+',
                      lambda m: '<ul>\n' + m.group(0).replace('<UL_ITEM>', '<li>').replace('</UL_ITEM>', '</li>') + '</ul>\n',
                      text, flags=re.DOTALL)

        lines = text.split('\n')
        out = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('<'):
                out.append(f'<p>{line}</p>')
            else:
                out.append(line)
        return '\n'.join(out)
    except Exception as e:
        return f"<p>Render error: {e}</p>"


# --- UI layer ---

class BrowserWindow(QMainWindow):
    def __init__(self, screen_num, on_close):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window)
        self._on_close = on_close

        screens = QApplication.screens()
        idx = max(0, min(screen_num - 1, len(screens) - 1))
        geo = screens[idx].geometry()
        self.setGeometry(geo)

        self.view = QWebEngineView()
        self.setCentralWidget(self.view)
        self.show()
        self.setGeometry(geo)

    def set_title(self, title):
        self.setWindowTitle(title)

    def render_html(self, html):
        self.view.setHtml(html)

    def render_url(self, url):
        self.view.load(url)

    def closeEvent(self, event):
        self._on_close()
        super().closeEvent(event)


# --- Logic layer ---

class BrowserController:
    def __init__(self, screen_num, browser_id, content_path, daemon):
        self.screen_num      = screen_num
        self.browser_id      = browser_id
        self.content_path    = Path(content_path) if content_path else None
        self.reminder_active = False
        self._daemon         = daemon

        self.window = BrowserWindow(screen_num, self._on_window_closed)
        self.window.set_title(
            self.content_path.name if self.content_path else f"Browser {browser_id}"
        )

        self._reload_timer = QTimer()
        self._reload_timer.setSingleShot(True)
        self._reload_timer.setInterval(150)
        self._reload_timer.timeout.connect(self._do_reload)

        self.fs_watcher = QFileSystemWatcher()
        self._setup_content_watcher()
        self.fs_watcher.fileChanged.connect(self._on_file_changed)

        self.reminder_watcher = QFileSystemWatcher()
        self.reminder_watcher.addPath("/tmp")
        self.reminder_watcher.directoryChanged.connect(self._on_reminder_dir_changed)

        self.load_default()
        self.refresh_reminder_state()

    def _setup_content_watcher(self):
        existing = self.fs_watcher.files()
        if existing:
            self.fs_watcher.removePaths(existing)
        if self.content_path and self.content_path.exists():
            self.fs_watcher.addPath(str(self.content_path))

    def load_default(self):
        if self.content_path and self.content_path.exists():
            try:
                text = self.content_path.read_text(encoding="utf-8")
                self.window.render_html(CONTENT_TEMPLATE.format(content=md_to_html(text)))
            except Exception as e:
                self.window.render_html(CONTENT_TEMPLATE.format(content=f"<p>Error: {e}</p>"))
        elif WALLPAPER.exists():
            self.window.render_url(QUrl.fromLocalFile(str(WALLPAPER)))
        else:
            self.window.render_html(CONTENT_TEMPLATE.format(content="<h1>Ready</h1>"))

    def _on_file_changed(self, path):
        if self.reminder_active or not self.content_path or not self.content_path.exists():
            return
        self._setup_content_watcher()
        self._reload_timer.start()

    def _do_reload(self):
        if not self.content_path or not self.content_path.exists():
            return
        history_dir = Path("/media/cade/F/file-history")
        if history_dir.exists():
            try:
                ts   = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                dest = history_dir / f"{self.content_path.stem}_{ts}{self.content_path.suffix}"
                dest.write_bytes(self.content_path.read_bytes())
                copies = sorted(history_dir.glob(f"{self.content_path.stem}_*{self.content_path.suffix}"))
                for old in copies[:-HISTORY_MAX]:
                    old.unlink(missing_ok=True)
            except Exception:
                pass
        self.load_default()

    def _on_reminder_dir_changed(self, _path):
        self.refresh_reminder_state()

    def refresh_reminder_state(self):
        exists = REMINDER_FILE.exists()
        if exists and not self.reminder_active:
            try:
                msg = REMINDER_FILE.read_text().strip() or "Time to move!"
            except Exception:
                msg = "Time to move!"
            self.window.render_html(DAGGER_HTML.format(msg=msg))
            self.reminder_active = True
        elif not exists and self.reminder_active:
            self.load_default()
            self.reminder_active = False

    def _on_window_closed(self):
        self._daemon.active_controllers.pop(self.browser_id, None)


# --- App layer ---

class BrowserDaemon(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)
        self.active_controllers = {}
        self._next_id = 1

        QLocalServer.removeServer(SOCKET_PATH)
        Path(SOCKET_PATH).unlink(missing_ok=True)
        self.server = QLocalServer(self)
        self.server.listen(SOCKET_PATH)
        self.server.newConnection.connect(self._on_connection)

    def _on_connection(self):
        conn = self.server.nextPendingConnection()
        conn.readyRead.connect(lambda: self._handle_request(conn))

    def _handle_request(self, conn):
        try:
            data = conn.readAll().data().decode()
            msg  = json.loads(data)
            self.open_window(msg.get("screen", 2), msg.get("file"))
            conn.write(b'{"ok":true}')
        except Exception as e:
            conn.write(json.dumps({"ok": False, "error": str(e)}).encode())
        conn.flush()
        conn.disconnectFromServer()

    def open_window(self, screen_num, file_path=None):
        if len(self.active_controllers) >= WINDOW_CAP:
            print(
                f"ERROR: browser window cap ({WINDOW_CAP}) reached — "
                "close existing windows or restart the daemon",
                file=sys.stderr,
            )
            return
        browser_id = self._next_id
        self._next_id += 1
        ctrl = BrowserController(screen_num, browser_id, file_path, self)
        self.active_controllers[browser_id] = ctrl


def try_send_to_daemon(screen, file_path):
    for attempt in range(3):
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect(SOCKET_PATH)
            msg = json.dumps({"screen": screen, "file": file_path})
            sock.sendall(msg.encode())
            sock.close()
            return True
        except (OSError, socket.error):
            if attempt < 2:
                time.sleep(0.1)
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent browser")
    parser.add_argument("screen", type=int, help="Screen number (1, 2, 3...)")
    parser.add_argument("file",   nargs="?", default=None, help="Optional file to display")
    args = parser.parse_args()

    if try_send_to_daemon(args.screen, args.file):
        sys.exit(0)

    daemon = BrowserDaemon(sys.argv)
    daemon.open_window(args.screen, args.file)
    sys.exit(daemon.exec())
