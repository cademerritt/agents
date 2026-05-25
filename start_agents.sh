#!/bin/bash
bash /home/cade/agents/mouse-settings.sh &

pkill -f screenshot_agent.py 2>/dev/null
DISPLAY=:0 python3 /home/cade/agents/screenshot_agent.py &
