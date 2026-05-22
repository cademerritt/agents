# Hourly Backup Plan v7

## How It Runs
1. Hook-based — fires on first message after each new hour
2. Hook spawns detached double-fork worker and returns immediately — prompt never waits
3. Timestamp written before forking — prevents duplicate runs
4. No daemon, no cron, no background compute
5. UTC epoch timestamp comparison

## What Gets Backed Up
- All files changed anywhere on the system
- Scan root: `/` (entire filesystem)
- Does not cross filesystem boundaries (device ID check — stays on root partition only)
- Permission errors skipped gracefully — scan keeps going
- Exclusions: /proc, /sys, /dev, /run, /tmp, /media/cade/F
- Also exclude: .cache, venv, .venv, node_modules, __pycache__, .git, .nv, browser cache

## How Files Are Copied
- `shutil.copy2()` — preserves mtime and permissions
- All backed-up files made immutable with `chattr +i`
- Applied only after successful copy
- Applied to files only, never directories
- Requires sudoers rule: `cade ALL=(ALL) NOPASSWD: /usr/bin/chattr`

## Manifest Log
- Written to `manifest.txt.tmp` first, then renamed to `manifest.txt` (atomic — no partial manifests on crash)
- Contains: file path, size, mtime, SHA256 hash, copy timestamp
- Made immutable along with all other backup files

## F Drive Rule
- Immutable record of everything — if something goes wrong, recover from F drive
- Write once. Nothing is ever deleted, pruned, or modified.
- Files go in and stay forever.

## Two Files
- `hourly_backup.py` — harness: checks timestamp, spawns worker, outputs JSON context
- `hourly_backup_worker.py` — engine: walks filesystem, copies files, writes manifest

## Hook Integration
- Merged into existing `user_prompt_hook.py` — does not replace it
- Backup context injected into hookSpecificOutput.additionalContext
- Existing CLAUDE.md every-5-messages injection preserved

## Storage
- `/media/cade/F/backups/YYYY-MM-DD_HH-00/`
- Timestamp: `/home/cade/.last_backup_time`
