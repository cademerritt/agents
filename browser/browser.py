#!/usr/bin/env python3
import sys
import os
import re
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from datetime import datetime
from PyQt6.QtCore import QTimer, Qt, QUrl, QFileSystemWatcher

SCREENS = {
    1: (0,    0,   1920, 1080),
    2: (1920, 529, 1920, 1200),
    3: (3840, 649, 1920, 1080),
}

REMINDER_FILE = Path("/tmp/reminder.txt")

WALLPAPER = Path("/home/cade/.local/share/backgrounds/2026-04-18-17-10-32-Picture1.png")

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
  p {{ margin:7px 0; }}
  strong {{ color:#e5c07b; }}
  a {{ color:#61afef; }}
  hr {{ border:none; border-top:1px solid #333; margin:20px 0; }}
</style></head>
<body>{content}</body></html>"""


def md_to_html(text):
    # escape HTML special chars first
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # fenced code blocks
    def replace_code_block(m):
        lang = m.group(1) or ""
        code = m.group(2)
        return f'<pre><code class="language-{lang}">{code}</code></pre>'
    text = re.sub(r'```(\w*)\n(.*?)```', replace_code_block, text, flags=re.DOTALL)

    # inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # headers
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$',  r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$',   r'<h1>\1</h1>', text, flags=re.MULTILINE)

    # bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

    # horizontal rule
    text = re.sub(r'^---$', r'<hr>', text, flags=re.MULTILINE)

    # numbered lists → <ol>
    text = re.sub(r'^\d+\. (.+)$', r'<OL_ITEM>\1</OL_ITEM>', text, flags=re.MULTILINE)
    text = re.sub(r'(<OL_ITEM>.*?</OL_ITEM>\n{0,2})+',
                  lambda m: '<ol>\n' + m.group(0).replace('<OL_ITEM>', '<li>').replace('</OL_ITEM>', '</li>') + '</ol>\n',
                  text, flags=re.DOTALL)

    # bullet lists → <ol> (always numbered)
    text = re.sub(r'^[-*] (.+)$', r'<UL_ITEM>\1</UL_ITEM>', text, flags=re.MULTILINE)
    text = re.sub(r'(<UL_ITEM>.*?</UL_ITEM>\n{0,2})+',
                  lambda m: '<ol>\n' + m.group(0).replace('<UL_ITEM>', '<li>').replace('</UL_ITEM>', '</li>') + '</ol>\n',
                  text, flags=re.DOTALL)

    # plain lines → paragraphs (skip lines already wrapped in tags)
    lines = text.split('\n')
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('<'):
            out.append(f'<p>{line}</p>')
        else:
            out.append(line)
    return '\n'.join(out)


class BrowserWindow(QMainWindow):
    def __init__(self, screen_num, content_path=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window)
        x, y, w, h = SCREENS[screen_num]
        self.setGeometry(x, y, w, h)
        self.content_path = Path(content_path) if content_path else None
        title = self.content_path.name if self.content_path else f"Browser — Screen {screen_num}"
        self.setWindowTitle(title)
        self.reminder_active = False

        self.view = QWebEngineView()
        self.setCentralWidget(self.view)

        self.load_default()
        self.show()
        self.setGeometry(x, y, w, h)

        # force window to correct screen coordinates after window manager settles
        QTimer.singleShot(800, lambda t=title, px=x, py=y, pw=w, ph=h: os.system(
            f'DISPLAY=:0 xdotool search --name "{t}" windowmove %1 {px} {py} windowsize %1 {pw} {ph}'
        ))

        self.fs_watcher = QFileSystemWatcher()
        if self.content_path and self.content_path.exists():
            self.fs_watcher.addPath(str(self.content_path))
        self.fs_watcher.fileChanged.connect(self.on_file_changed)

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_reminder)
        self.timer.start(3000)

    def load_default(self):
        if self.content_path and self.content_path.exists():
            text = self.content_path.read_text(encoding="utf-8")
            content = md_to_html(text)
            html = CONTENT_TEMPLATE.format(content=content)
            self.view.setHtml(html)
        else:
            self.view.load(QUrl.fromLocalFile(str(WALLPAPER)))

    def on_file_changed(self, path):
        if self.reminder_active or not self.content_path or not self.content_path.exists():
            return
        self.fs_watcher.addPath(str(self.content_path))
        history_dir = Path("/media/cade/F/file-history")
        if history_dir.exists():
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            dest = history_dir / f"{self.content_path.stem}_{ts}{self.content_path.suffix}"
            dest.write_bytes(self.content_path.read_bytes())
        self.load_default()

    def check_reminder(self):
        exists = REMINDER_FILE.exists()
        if exists and not self.reminder_active:
            msg = REMINDER_FILE.read_text().strip() or "Time to move!"
            self.view.setHtml(DAGGER_HTML.format(msg=msg))
            self.reminder_active = True
        elif not exists and self.reminder_active:
            self.load_default()
            self.reminder_active = False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: browser.py <screen_num> [file_path]")
        sys.exit(1)

    screen_num = int(sys.argv[1])
    if screen_num not in SCREENS:
        print("Screen must be 1, 2, or 3")
        sys.exit(1)

    content_path = sys.argv[2] if len(sys.argv) > 2 else None

    app = QApplication(sys.argv)
    window = BrowserWindow(screen_num, content_path)
    sys.exit(app.exec())
