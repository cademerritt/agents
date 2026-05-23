---
name: System Hardware Reference
description: Physical machine specs — drives, GPU, monitors, dual-boot layout
type: reference
originSessionId: c1b4fc12-8eb4-43d8-aa1a-fe26c1bdfc7a
---
## Drives

1. **nvme0n1** — 1.8TB — C drive (Windows SSD, not mounted in Linux)
   - p1: 100MB vfat — Windows EFI
   - p2: 16MB — Microsoft Reserved
   - p3: 1.8TB NTFS "MAIN" — Windows OS
   - p4: 842MB NTFS — Windows Recovery

2. **nvme1n1** — 1.8TB — E drive (Linux SSD)
   - p1: 1GB vfat — /boot/efi
   - p2: 1.8TB ext4 — Linux root (/)

3. **sda1** — 18.2TB ext4 — Immutable Drive (label: ImmutableDrive) — mounted at /media/cade/ImmutableDrive
   - Used for: file history, snapshots, backups, system settings, AI models (future)
   - All files carry chattr +i immutable flag

## GPU

- Primary: GTX 1070 Ti
- Second GPU: installed (large PCIe slot)

## Monitors

- 3 monitors
- Screen 1: Claude Code (VSCode)
- Screen 2: Terminal
- Screen 3: Chrome (email, GitHub, Claude)

## Dual Boot

- Windows/Linux on separate NVMe drives
- Linux: Ubuntu
- Boot selects which NVMe to use
