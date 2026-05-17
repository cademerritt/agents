---
description: Open agent browser on screens 2 and 3
---

Open the agent browser on screen 2 and screen 3.

```bash
source ~/venv/bin/activate && DISPLAY=:0 python /media/cade/E/agents/browser/browser.py 2 2>/dev/null &
```

```bash
source ~/venv/bin/activate && DISPLAY=:0 python /media/cade/E/agents/browser/browser.py 3 2>/dev/null &
```
