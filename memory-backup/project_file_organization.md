---
name: File organization problem
description: Cade's machine has files scattered across drives causing instability with Claude browser and Claude Code
type: project
originSessionId: dc4a23b4-fe27-47e7-bc00-221eb97dff97
---
Critical file organization issue needs to be resolved before next session.

**Drive layout:**
- C drive / main Linux OS = nvme0n1p4 (1.8TB ext4, mounted at /)
- E drive = nvme0n1p2 (2.2GB FAT32, mounted at /media/cade/E) — this is tiny, NOT the full 2TB SSD. Linux lives on E drive.
- F drive = sda1 (19TB NTFS, mounted at /media/cade/F) — large storage HDD
- nvme1n1 = 1.8TB NTFS (Windows drive, not mounted in Linux)

**Current mess:**
- Python scripts in ~/PyProjects (main drive)
- venv in ~/venv (main drive, 10GB+)
- Ollama models pointed at /media/cade/E/ollama (2.2GB FAT32 — will fill up fast)
- Piper voice models in /media/cade/E/piper-voices

**Problems caused:**
- Files scattered across drives caused Claude browser to behave erratically
- Claude Code was also affected until fixed today
- FAT32 on E drive doesn't support Linux file permissions (chown fails)
- Ollama service had permission errors because of FAT32

**Plan for next session:**
- Decide proper home for: venv, models, scripts, data
- F drive (19TB NTFS) is best for large model files
- Need to verify where Ollama models actually landed (may have failed due to FAT32 issues)
- Reorganize before adding more components to the assistant

**Why:** File scatter is causing instability across all Claude interfaces. Need a clean, intentional layout before building further.
**How to apply:** Before installing anything new, confirm target drive and check permissions support first.
