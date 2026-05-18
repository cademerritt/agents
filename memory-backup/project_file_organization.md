---
name: File organization problem
description: Cade's machine has files scattered across drives causing instability with Claude browser and Claude Code
type: project
originSessionId: dc4a23b4-fe27-47e7-bc00-221eb97dff97
---
Critical file organization issue needs to be resolved before next session.
**Drive layout:**
1. nvme0n1 — 1.8TB — C drive (Windows SSD, not mounted in Linux) — p1: 100MB vfat Windows EFI — p2: 16MB Microsoft Reserved — p3: 1.8TB NTFS "MAIN" Windows OS — p4: 842MB NTFS Windows Recovery
2. nvme1n1 — 1.8TB — E drive — p1: 1GB vfat /boot/efi — p2: 1.8TB ext4 Linux root
3. sda1 — 18.2TB ext4 — F drive — /media/cade/F

**To-Do / Plan for next session:**
1. Make file watchers less compute-hungry (replace polling timers with inotify)
2. Rebuild CLAUDE.md
3. Rebuild start_agents.sh
4. Build multi-LLM conversation agent (route questions to Gemini/ChatGPT/Claude simultaneously for consensus diagnosis)
5. Review MEMORY.md structure — decide whether session files belong in MEMORY.md index or should be consolidated into project_file_organization.md
6. After second GPU install: verify system recognizes it and all programs run normally
7. Reassign F6 (mic), F7 (send screenshot), F8 (take screenshot) from function keys to numpad keys — numpad arrives from B&H today
8. Rewrite permission rule (feedback_permission_rule.md) — explicit command = permission for that action only
9. Define catchphrase/explicit-command system — specific known command phrases (e.g. "t the latest screenshot") are self-authorizing; no separate permission ask needed
10. Assign end chat to a numpad key — key triggers mic on; say "end chat" to confirm and proceed, say "no" to cancel

**Plans for the future:**
1. Install second GPU in large PCIe slot when ready — DOING TODAY
2. Set up dedicated 2TB SSD for Ollama/AI models when ready
3. Restore Piper voice models from F drive backup to F drive (not E)
4. Third GPU external housing — mini-ITX case + PCIe riser cable approach (deferred)
