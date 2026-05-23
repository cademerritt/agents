---
name: System Software Reference
description: OS, Python versions, venv, installed packages, key agent paths
type: reference
originSessionId: c1b4fc12-8eb4-43d8-aa1a-fe26c1bdfc7a
---
## Operating Systems

- **Linux:** Ubuntu (primary daily driver)
- **Windows:** dual boot on separate NVMe (nvme0n1)

## Python

- Linux: Python 3.12
- Windows: Python 3.14
- Virtual environment: `~/venv` — always activate before running Python on Linux (`source ~/venv/bin/activate`)

## Daily Software Setup

- **Claude Pro** — subscription tier
- **VSCode** — screen 1, runs Claude Code
- **Terminal** — screen 2
- **Chrome** — screen 3 (email, GitHub, Claude web)

## Key Paths

- Agents: `/home/cade/agents/` — browser, hotkey_daemon, screenshot_agent
- Claude Code: VSCode on screen 1
- F drive settings: `/media/cade/ImmutableDrive/system-settings/`
- File history: `/media/cade/ImmutableDrive/file-history/`
- Snapshots: `/media/cade/ImmutableDrive/snapshots/`

## Full Package / Driver List

See: `/media/cade/ImmutableDrive/system-settings/packages-and-drivers.txt`
Includes: Nvidia driver, apt packages, pip packages

## GitHub

- Username: cademerritt
- Token: `~/.github_token` and `~/.git-credentials`
- All work pushed to GitHub after every session
