#!/usr/bin/env python3
import subprocess
import threading
import re
import tkinter as tk
from tkinter import scrolledtext

BG         = "#141414"
FG         = "#ffffff"
INPUT_BG   = "#252526"
ORANGE     = "#e8a045"
SIDEBAR_BG = "#1e1e1e"
BAR_BG     = "#ffffff"
RADIUS     = 12
FONT       = ("Courier", 14)
FONT_SM    = ("Courier", 13)
SIDEBAR_W  = 40
BAR_H      = 28


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


class RoundedInput:
    def __init__(self, parent, width=900, height=90, on_submit=None):
        self.width     = width
        self.height    = height
        self.on_submit = on_submit

        self.canvas = tk.Canvas(parent, width=width, height=height,
                                bg=BG, highlightthickness=0, bd=0)
        self.canvas.pack()

        self._draw_rounded_rect(INPUT_BG, INPUT_BG, glow=False)

        inset = RADIUS + 4
        self.text = tk.Text(self.canvas, bg=INPUT_BG, fg=FG, font=FONT_SM,
                            insertbackground=FG, wrap=tk.WORD,
                            relief=tk.FLAT, padx=10, pady=8,
                            height=3, borderwidth=0, highlightthickness=0)
        self.canvas.create_window(width // 2, height // 2,
                                  window=self.text,
                                  width=width - inset * 2,
                                  height=height - inset * 2)

        self.text.bind("<FocusIn>",      lambda e: self._draw_rounded_rect(INPUT_BG, ORANGE, glow=True))
        self.text.bind("<FocusOut>",     lambda e: self._draw_rounded_rect(INPUT_BG, INPUT_BG, glow=False))
        self.text.bind("<Return>",       self._handle_return)
        self.text.bind("<Shift-Return>", lambda e: None)

    def _draw_rounded_rect(self, fill, outline, glow=False):
        self.canvas.delete("rr")
        r = RADIUS
        w, h = self.width, self.height

        # glow layers
        if glow:
            for i in range(6, 0, -1):
                alpha_color = ORANGE
                pts = [
                    r+i, i,  w-r-i, i,
                    w-i, r+i,  w-i, h-r-i,
                    w-r-i, h-i,  r+i, h-i,
                    i, h-r-i,  i, r+i
                ]
                self.canvas.create_polygon(pts, smooth=True,
                                           fill="", outline=alpha_color,
                                           width=1, tags="rr")

        pts = [
            r, 0,  w-r, 0,
            w, r,  w, h-r,
            w-r, h,  r, h,
            0, h-r,  0, r
        ]
        self.canvas.create_polygon(pts, smooth=True,
                                   fill=fill, outline=outline,
                                   width=2, tags="rr")
        self.canvas.tag_lower("rr")

    def _handle_return(self, event):
        if self.on_submit:
            msg = self.text.get("1.0", tk.END).strip()
            if msg:
                self.text.delete("1.0", tk.END)
                self.on_submit(msg)
        return "break"


class CCBrowser:
    def __init__(self, screen_num=2):
        self.root = tk.Tk()
        self.root.title("CC Browser")
        self.root.configure(bg=BG)

        geo = get_screen_geometry(screen_num)
        if geo:
            self.root.geometry(geo)

        # ── bottom bar (must pack before sidebar) ─────────────
        bottom_bar = tk.Frame(self.root, bg=BAR_BG, height=BAR_H)
        bottom_bar.pack(side=tk.BOTTOM, fill=tk.X)
        bottom_bar.pack_propagate(False)

        # ── left sidebar ──────────────────────────────────────
        sidebar = tk.Frame(self.root, bg=SIDEBAR_BG, width=SIDEBAR_W)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # ── main area ─────────────────────────────────────────
        main = tk.Frame(self.root, bg=BG)
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # conversation display
        self.display = scrolledtext.ScrolledText(
            main, bg=BG, fg=FG, font=FONT,
            insertbackground=FG, wrap=tk.WORD,
            relief=tk.FLAT, padx=24, pady=24,
            state=tk.DISABLED
        )
        self.display.pack(fill=tk.BOTH, expand=True)

        # input area
        input_area = tk.Frame(main, bg=BG, pady=16)
        input_area.pack(fill=tk.X)
        self.input = RoundedInput(input_area, width=900, height=90,
                                  on_submit=self.send_message)

        # ── claude subprocess ─────────────────────────────────
        self.proc = subprocess.Popen(
            ["claude", "--output-format", "stream-json",
             "--input-format", "stream-json", "--no-chrome"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1
        )

        threading.Thread(target=self._read_output, daemon=True).start()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _append(self, text):
        self.display.config(state=tk.NORMAL)
        self.display.insert(tk.END, text)
        self.display.see(tk.END)
        self.display.config(state=tk.DISABLED)

    def send_message(self, msg):
        self._append(f"\nYou: {msg}\n")
        try:
            self.proc.stdin.write(msg + "\n")
            self.proc.stdin.flush()
        except Exception as e:
            self._append(f"[Error: {e}]\n")

    def _read_output(self):
        import json
        for line in self.proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if obj.get("type") == "message_start":
                    self.root.after(0, self._append, "\nClaude: ")
                elif obj.get("type") == "content_block_delta":
                    delta = obj.get("delta", {})
                    if delta.get("type") == "text_delta":
                        self.root.after(0, self._append, delta.get("text", ""))
                elif obj.get("type") == "message_stop":
                    self.root.after(0, self._append, "\n")
            except Exception:
                self.root.after(0, self._append, line + "\n")

    def _on_close(self):
        try:
            self.proc.terminate()
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    import sys
    screen = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    CCBrowser(screen)
