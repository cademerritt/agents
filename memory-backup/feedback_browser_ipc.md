---
name: Browser IPC mechanism
description: How to send a file to the browser on screen 2 or 3
type: feedback
originSessionId: 9b868149-ebdf-4636-b75e-d5bf14c4b20f
---
The browser has NO external IPC socket. To change what it displays, kill it and relaunch with the new file path:

```bash
PID=$(pgrep -f "python.*personal_browser.py 3"); [ -n "$PID" ] && kill $PID; sleep 1
source ~/venv/bin/activate && DISPLAY=:0 python /home/cade/agents/browser/personal_browser.py 3 /path/to/file.md 2>/dev/null &
```

Replace `3` with `2` for screen 2.

**Why:** The browser polls its initial file_path for changes (every 1s) but has no mechanism to receive a new file path after launch. The only way to switch files is restart.

**How to apply:** Any time the user asks to show a file in the browser on screen 2 or 3, just kill and relaunch. Don't search for sockets or IPC — there aren't any.
