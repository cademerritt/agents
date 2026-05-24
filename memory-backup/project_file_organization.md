---
name: Session To-Do List
description: Active to-do list and plans for upcoming sessions
type: project
originSessionId: c1b4fc12-8eb4-43d8-aa1a-fe26c1bdfc7a
---
**Mid-Session State (May 22 2026 ~7:52 PM — RESUME HERE):**
- Screen 1: VSCode with Claude Code
- Screen 2: Browser showing Hourly Backup Plan v7 — file saved at `/home/cade/agents/hourly-backup-plan-v7.md`
- Screen 3: Chrome
- In progress: LLM consensus on hourly backup agent — ChatGPT agreed with v7, Perplexity agreed, Gemini not yet reviewed v7
- Next step: Send v7 to Gemini, get consensus, then write the code
- Sudoers rule still needed: `cade ALL=(ALL) NOPASSWD: /usr/bin/chattr`

**To-Do / Plan for next session:**
1. [FIRST TOMORROW] LLM consensus on browser.py rewrite — get opinions from Gemini, ChatGPT, Perplexity
2. [TOP PRIORITY] Build sensor agent — monitors CPU, GPU, and motherboard temps continuously; alerts when temps are high; runs as background daemon; reports to Claude on demand
3. Rebuild CLAUDE.md
4. Rebuild start_agents.sh
5. Build multi-LLM conversation agent (route questions to Gemini/ChatGPT/Claude simultaneously for consensus diagnosis)
6. Review MEMORY.md structure — decide whether session files belong in MEMORY.md index or should be consolidated into project_file_organization.md
7. After second GPU install: verify system recognizes it and all programs run normally
8. Rewrite permission rule (feedback_permission_rule.md) — explicit command = permission for that action only
9. Define catchphrase/explicit-command system — specific known command phrases (e.g. "t the latest screenshot") are self-authorizing; no separate permission ask needed
10. Assign end chat to a numpad key — key triggers mic on; say "end chat" to confirm and proceed, say "no" to cancel
11. Build consensus agent — a Claude chat/agent that already knows the existing hook setup, file structure, and Claude-specific context, so it can filter out ignorant suggestions from external LLMs (ChatGPT, Gemini, Perplexity) before they reach the user

**Plans for the future:**
1. Install second GPU in large PCIe slot when ready — DOING TODAY
2. Set up dedicated 2TB SSD for Ollama/AI models when ready
3. Restore Piper voice models from F drive backup to F drive (not E)
4. Third GPU external housing — mini-ITX case + PCIe riser cable approach (deferred)
