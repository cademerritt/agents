---
name: Global Renames Log
description: Log of all file/script renames — check here first when something breaks after a rename
type: reference
originSessionId: c1b4fc12-8eb4-43d8-aa1a-fe26c1bdfc7a
---
## How to use
If something breaks and you suspect a rename is the cause, check this file for what was changed and which files were updated. If a reference was missed, it will be listed as "not updated."

---

## Renames

### browser.py → personal_browser.py
**Date:** May 23, 2026
**Old path:** `/home/cade/agents/browser/browser.py`
**New path:** `/home/cade/agents/browser/personal_browser.py`

**Files updated:**
- `/home/cade/.claude/settings.json` — SessionEnd pkill command
- `/home/cade/agents/settings.json` — SessionEnd pkill command
- `/home/cade/.claude/projects/-home-cade/memory/feedback_browser_ipc.md` — kill/launch commands
- `/home/cade/agents/commands/open-browser-1.md` — launch command + path corrected (was E drive)
- `/home/cade/agents/commands/open-browser-2.md` — launch command + path corrected (was E drive)
- `/home/cade/agents/commands/open-browser-3.md` — launch command + path corrected (was E drive)
- `/home/cade/agents/commands/open-browsers.md` — launch commands + paths corrected (was E drive)

**Not updated (historical records only):**
- All session-05-*.md files — documentation, not functional

---

### F drive label → ImmutableDrive (mount path: /media/cade/F → /media/cade/ImmutableDrive)
**Date:** May 23, 2026
**Command run:** `sudo e2label /dev/sda1 ImmutableDrive`
**Old mount:** `/media/cade/F`
**New mount:** `/media/cade/ImmutableDrive`

**Files updated (global sed replace):**
- `/home/cade/agents/hourly-backup-plan-v7.md` through `v10.md`
- `/home/cade/agents/screenshot_agent.py`
- `/home/cade/agents/f7_watcher.py`
- `/home/cade/agents/send_screenshot.py`
- `/home/cade/agents/hooks/session_start_check.py`
- `/home/cade/agents/hooks/session_backup.py`
- `/home/cade/agents/browser/personal_browser.py`
- `/home/cade/.claude/projects/-home-cade/memory/system_architecture/reference_system_hardware.md`
- `/home/cade/.claude/projects/-home-cade/memory/system_architecture/reference_system_software.md`
- `/home/cade/.claude/projects/-home-cade/memory/reference_packages_drivers.md`
- `/home/cade/.claude/projects/-home-cade/memory/MEMORY.md`
- All memory-backup/ copies of the above

**Not updated (historical records only):**
- All session-05-*.md files — documentation, not functional
