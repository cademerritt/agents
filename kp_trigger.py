#!/usr/bin/env python3
import socket
import sys

SOCK_PATH = "/tmp/screenshot_agent.sock"


def main():
    if len(sys.argv) < 2:
        return
    cmd = sys.argv[1]
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(SOCK_PATH)
        s.sendall(cmd.encode())
        s.close()
    except Exception:
        pass


if __name__ == "__main__":
    main()
