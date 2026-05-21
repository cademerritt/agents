# LLM Consensus Scores

A running record of how Claude, ChatGPT, Gemini, and Perplexity perform across tasks.
Used to inform agent design decisions.

---

## Coding

**Task: Replace QTimer polling with QFileSystemWatcher in browser.py (May 20, 2026)**

| LLM | Grade | Notes |
|---|---|---|
| Perplexity | A | Cleanest structure — `refresh_reminder_state()` separation, correct logic, wrong import (PySide6 vs PyQt6) |
| Gemini | B+ | Correct PyQt6 import, dual-watch approach (directory + file), slightly over-engineered for this use case |
| ChatGPT | B | Directory-only watch (correct for this case), wrong import (PyQt5), caught atomic replace issue |
| Claude | B+ | Same core approach as consensus, would have skipped `refresh_reminder_state()` without Perplexity's example |

**Winner: Perplexity**

**Takeaway:** Consensus process produced a better-validated solution. Three independent LLMs agreeing on directory-only watching confirmed the approach. Perplexity's method naming was the clearest.

---

## Agent Design Notes

- Perplexity tends toward clean, readable structure
- Gemini tends toward thoroughness and edge-case coverage
- ChatGPT catches practical issues (atomic replace) but may use outdated imports
- Consensus rounds are worth running for any non-trivial code decision
