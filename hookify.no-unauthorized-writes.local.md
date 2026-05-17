---
name: no-unauthorized-writes
enabled: true
event: bash
action: block
pattern: (Edit|Write|write|create|overwrite)
---

BLOCK: Do not write, edit, or create any file without first explaining exactly what you are about to do and receiving explicit permission from Cade.
