---
name: activate-venv
enabled: true
event: bash
pattern: (?<!source ~/venv/bin/activate && )(^|\s)(python|pip|pip3|python3)\s
action: block
---

BLOCK: Always activate the virtual environment before running any Python or pip command on Linux. Use: source ~/venv/bin/activate
