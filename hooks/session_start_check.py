#!/usr/bin/env python3
import os
import subprocess
import shutil
import difflib
from pathlib import Path
from datetime import datetime

SNAPSHOTS_DIR = Path("/home/cade/agents/snapshots")
MAX_SNAPSHOTS = 5

SYSTEM_FILES = [
    Path("/etc/default/grub"),
    Path("/etc/fstab"),
    Path("/etc/gdm3/custom.conf"),
    Path("/home/cade/.config/monitors.xml"),
    Path("/home/cade/.config/gtk-3.0/bookmarks"),
    Path("/etc/udev/rules.d/99-hide-partitions.rules"),
]

FILE_LABELS = {
    "dconf.conf": "GNOME settings (dock, wallpaper, display, shortcuts)",
    "grub": "Boot menu (GRUB)",
    "fstab": "Drive mounts (fstab)",
    "custom.conf": "Auto-login (GDM)",
    "monitors.xml": "Monitor layout and orientation",
    "bookmarks": "File manager sidebar",
    "nvidia-driver.txt": "Nvidia driver version",
    "99-hide-partitions.rules": "Hidden partition rules (udev)",
    "packages.txt": "Installed packages",
}

def capture_snapshot(dest: Path):
    dest.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(["dconf", "dump", "/"], capture_output=True, text=True)
    (dest / "dconf.conf").write_text(result.stdout)

    for fpath in SYSTEM_FILES:
        if fpath.exists():
            shutil.copy2(str(fpath), str(dest / fpath.name))

    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
        capture_output=True, text=True)
    (dest / "nvidia-driver.txt").write_text(result.stdout.strip())

    result = subprocess.run(["dpkg", "--get-selections"], capture_output=True, text=True)
    (dest / "packages.txt").write_text(result.stdout)

    (dest / "timestamp.txt").write_text(datetime.now().isoformat())

def get_snapshots():
    if not SNAPSHOTS_DIR.exists():
        return []
    return sorted([d for d in SNAPSHOTS_DIR.iterdir()
                   if d.is_dir() and d.name.startswith("snap-")])

def rotate_snapshots():
    snapshots = get_snapshots()
    while len(snapshots) >= MAX_SNAPSHOTS:
        shutil.rmtree(str(snapshots[0]))
        snapshots = snapshots[1:]

def summarize_diff(fname, prev_text, curr_text):
    if fname == "nvidia-driver.txt":
        return f"driver changed: {prev_text.strip()} → {curr_text.strip()}"
    if fname == "packages.txt":
        prev = set(prev_text.splitlines())
        curr = set(curr_text.splitlines())
        added = curr - prev
        removed = prev - curr
        parts = []
        if added:
            parts.append(f"{len(added)} package(s) added")
        if removed:
            parts.append(f"{len(removed)} package(s) removed")
        return ", ".join(parts) if parts else "changed"
    diff = list(difflib.unified_diff(
        prev_text.splitlines(), curr_text.splitlines(), lineterm=""))
    added = [l[1:] for l in diff if l.startswith("+") and not l.startswith("+++")]
    removed = [l[1:] for l in diff if l.startswith("-") and not l.startswith("---")]
    parts = []
    if removed:
        parts.append(f"removed: {'; '.join(removed[:2])}")
    if added:
        parts.append(f"added: {'; '.join(added[:2])}")
    return " | ".join(parts) if parts else "changed"

def diff_snapshots(prev: Path, curr: Path):
    changes = []
    all_files = set(f.name for f in prev.iterdir()) | set(f.name for f in curr.iterdir())
    all_files.discard("timestamp.txt")
    for fname in sorted(all_files):
        p = prev / fname
        c = curr / fname
        p_text = p.read_text() if p.exists() else ""
        c_text = c.read_text() if c.exists() else ""
        if p_text != c_text:
            label = FILE_LABELS.get(fname, fname)
            summary = summarize_diff(fname, p_text, c_text)
            changes.append((label, summary))
    return changes

def parse_timestamp(snap: Path):
    try:
        ts = (snap / "timestamp.txt").read_text().strip()
        return datetime.fromisoformat(ts).strftime("%b %d at %I:%M %p")
    except Exception:
        return snap.name.replace("snap-", "")

def main():
    if not SNAPSHOTS_DIR.exists():
        try:
            SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"[settings check] F drive not available: {e}")
            return

    snapshots = get_snapshots()
    prev = snapshots[-1] if snapshots else None

    rotate_snapshots()
    timestamp = datetime.now().strftime("snap-%Y-%m-%d-%H%M%S")
    curr = SNAPSHOTS_DIR / timestamp
    capture_snapshot(curr)

    if prev is None:
        print("[settings check] First snapshot saved. Will compare from next session.")
        return

    changes = diff_snapshots(prev, curr)
    when = parse_timestamp(prev)

    if not changes:
        print(f"[settings check] All settings match last session ({when}). Nothing changed.")
    else:
        print(f"[settings check] {len(changes)} change(s) since {when}:")
        for label, summary in changes:
            print(f"  • {label}: {summary}")
        print("[settings check] Review with Cade before proceeding.")

if __name__ == "__main__":
    main()
