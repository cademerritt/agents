---
name: System Rebuild Reference
description: Location of the full package and driver list needed to rebuild after a drive wipe
type: reference
originSessionId: c1b4fc12-8eb4-43d8-aa1a-fe26c1bdfc7a
---
Full system rebuild package list is at:
**/media/cade/ImmutableDrive/system-settings/packages-and-drivers.txt**

Contains three sections:
1. Nvidia driver version
2. All apt packages (dpkg --get-selections)
3. All pip packages in /home/cade/venv (pip freeze)

To reinstall pip packages after a wipe:
`source /home/cade/venv/bin/activate && pip install -r <extracted pip section>`

Update this file whenever new packages are installed.
