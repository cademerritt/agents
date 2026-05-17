#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import cairo
import math
from datetime import datetime
from pathlib import Path
import time

SAVE_DIR = Path("/media/cade/F/screenshots")
F_DRIVE = Path("/media/cade/F")


def f_drive_mounted():
    return F_DRIVE.is_mount()


def show_error(msg):
    dialog = Gtk.MessageDialog(
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text=msg
    )
    dialog.run()
    dialog.destroy()


def get_monitors():
    display = Gdk.Display.get_default()
    monitors = []
    for i in range(display.get_n_monitors()):
        geo = display.get_monitor(i).get_geometry()
        monitors.append((geo.x, geo.y, geo.width, geo.height))
    return monitors


def find_monitor(monitors, click_x, click_y):
    for (x, y, w, h) in monitors:
        if x <= click_x < x + w and y <= click_y < y + h:
            return (x, y, w, h)
    return None


def capture_monitor(x, y, w, h):
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    filename = str(SAVE_DIR / f"Screenshot from {timestamp}.png")
    root = Gdk.get_default_root_window()
    while Gtk.events_pending():
        Gtk.main_iteration()
    pixbuf = Gdk.pixbuf_get_from_window(root, x, y, w, h)
    if pixbuf:
        pixbuf.savev(filename, 'png', [], [])
        print(f"[screenshot] Saved: {filename}")
    else:
        print("[screenshot] Capture failed")
    return filename


class RippleOverlay(Gtk.Window):
    def __init__(self, monitors):
        super().__init__()
        self.monitors = monitors
        self.ripples = []
        self.done = False

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        self.set_app_paintable(True)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)

        min_x = min(m[0] for m in monitors)
        min_y = min(m[1] for m in monitors)
        max_x = max(m[0] + m[2] for m in monitors)
        max_y = max(m[1] + m[3] for m in monitors)

        self.offset_x = min_x
        self.offset_y = min_y

        self.move(min_x, min_y)
        self.set_default_size(max_x - min_x, max_y - min_y)

        self.set_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK
        )

        self.connect('draw', self.on_draw)
        self.connect('button-press-event', self.on_click)
        self.connect('motion-notify-event', self.on_motion)

        seat = Gdk.Display.get_default().get_default_seat()
        pointer = seat.get_pointer()
        _, cx, cy = pointer.get_position()
        self.cursor_x = cx
        self.cursor_y = cy

        self.show_all()
        GLib.timeout_add(50, self.tick)

    def on_motion(self, widget, event):
        self.cursor_x = event.x_root
        self.cursor_y = event.y_root
        self.queue_draw()

    def tick(self):
        if self.done:
            return False
        now = time.time()
        if not self.ripples or now - self.ripples[-1][0] > 0.4:
            self.ripples.append((now, self.cursor_x, self.cursor_y))
        self.ripples = [r for r in self.ripples if now - r[0] < 1.0]
        self.queue_draw()
        return True

    def on_draw(self, widget, cr):
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        now = time.time()
        for (start, rx, ry) in self.ripples:
            age = now - start
            if age > 1.0:
                continue
            progress = age / 1.0
            radius = progress * 80
            alpha = (1.0 - progress) * 0.7
            lx = rx - self.offset_x
            ly = ry - self.offset_y
            cr.set_source_rgba(0.3, 0.85, 1.0, alpha)
            cr.set_line_width(2.5)
            cr.arc(lx, ly, radius, 0, 2 * math.pi)
            cr.stroke()

    def on_click(self, widget, event):
        if event.button == 1:
            click_x = int(event.x_root)
            click_y = int(event.y_root)
            monitor = find_monitor(self.monitors, click_x, click_y)
            self.done = True
            self.hide()
            if monitor:
                capture_monitor(*monitor)
            Gtk.main_quit()


def main():
    if not f_drive_mounted():
        show_error("F drive is not mounted — screenshot cancelled.\nPlease connect the F drive and try again.")
        return

    monitors = get_monitors()
    if not monitors:
        print("[screenshot] No monitors found")
        return
    overlay = RippleOverlay(monitors)
    Gtk.main()


if __name__ == '__main__':
    main()
