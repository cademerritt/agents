#!/usr/bin/env python3
import math
import re
import subprocess
import tkinter as tk

SIZE = 100
HALF = SIZE // 2


def get_mouse_pos():
    result = subprocess.run(["xdotool", "getmouselocation"], capture_output=True, text=True)
    m = re.match(r"x:(\d+) y:(\d+)", result.stdout)
    if m:
        return int(m.group(1)), int(m.group(2))
    return 0, 0


root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.7)
root.configure(bg="black")
root.geometry(f"{SIZE}x{SIZE}")

canvas = tk.Canvas(root, width=SIZE, height=SIZE, bg="black", highlightthickness=0)
canvas.pack()

tick = 0


def update():
    global tick
    mx, my = get_mouse_pos()
    root.geometry(f"+{mx - HALF}+{my - HALF}")
    canvas.delete("all")
    t = tick * 0.2
    for i, r in enumerate([12, 22, 34]):
        pulse = r + 5 * math.sin(t + i * 1.2)
        canvas.create_oval(
            HALF - pulse, HALF - pulse, HALF + pulse, HALF + pulse,
            outline="#4488ff", width=3
        )
    tick += 1
    root.after(50, update)


update()
root.mainloop()
