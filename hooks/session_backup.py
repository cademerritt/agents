#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

DEST_BASE = Path("/media/cade/F/backups")
SESSION_START_FILE = Path("/tmp/session_start_time")

WATCH_DIRS = [
    Path("/home/cade"),
    Path("/etc"),
]

GIT_REPOS = [
    Path("/home/cade/scripts"),
    Path("/home/cade/PyProjects"),
    Path("/home/cade/FILE-COMMANDER"),
    Path("/home/cade/COMMAND-FILES"),
    Path("/home/cade/cbre-app"),
    Path("/home/cade/folder-organizer"),
]

def fworm_backup(session_start):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    dest_dir = DEST_BASE / timestamp
    copied = 0
    errors = 0
    for watch_dir in WATCH_DIRS:
        if not watch_dir.exists():
            continue
        for root, dirs, files in os.walk(str(watch_dir)):
            for fname in files:
                fpath = Path(root) / fname
                try:
                    if fpath.stat().st_mtime > session_start:
                        rel = fpath.relative_to("/")
                        dest = dest_dir / rel
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(str(fpath), str(dest))
                        copied += 1
                except Exception:
                    errors += 1
    if copied > 0:
        print(f"F backup: {copied} files → {dest_dir} ({errors} errors)")
    else:
        print("F backup: no changed files")

def github_push():
    for repo in GIT_REPOS:
        if not repo.exists():
            continue
        try:
            subprocess.run(["git", "-C", str(repo), "pull", "--rebase"], capture_output=True)
            subprocess.run(["git", "-C", str(repo), "add", "-A"], capture_output=True)
            result = subprocess.run(["git", "-C", str(repo), "commit", "-m", "Session end auto-commit"], capture_output=True, text=True)
            if result.returncode == 0:
                subprocess.run(["git", "-C", str(repo), "push"], capture_output=True)
                print(f"GitHub pushed: {repo.name}")
            else:
                print(f"GitHub no changes: {repo.name}")
        except Exception as e:
            print(f"GitHub error ({repo.name}): {e}")

def main():
    if not SESSION_START_FILE.exists():
        print("No session start time — skipping backup")
        return
    session_start = float(SESSION_START_FILE.read_text().strip())
    fworm_backup(session_start)
    github_push()

if __name__ == "__main__":
    main()
