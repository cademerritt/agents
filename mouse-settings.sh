#!/bin/bash
sleep 2
MOUSE_ID=$(DISPLAY=:0 xinput list | grep "Compx 2.4G Receiver Mouse" | grep -o 'id=[0-9]*' | cut -d= -f2)
if [ -n "$MOUSE_ID" ]; then
    DISPLAY=:0 xinput set-prop "$MOUSE_ID" "libinput Accel Speed" -0.6
    DISPLAY=:0 xinput set-prop "$MOUSE_ID" "Coordinate Transformation Matrix" 1.5 0 0 0 1.5 0 0 0 1.0
fi
pkill xbindkeys 2>/dev/null; DISPLAY=:0 xbindkeys
pkill imwheel 2>/dev/null; DISPLAY=:0 imwheel
pkill -f mouse_forward_daemon 2>/dev/null
python3 /home/cade/agents/mouse_forward_daemon.py &
