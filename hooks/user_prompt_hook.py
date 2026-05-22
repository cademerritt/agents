#!/usr/bin/env python3
import sys
import json

CLAUDE_MD_PATH = "/home/cade/CLAUDE.md"
COUNTER_FILE = "/tmp/claude_msg_count"
INJECT_EVERY = 5

def get_count():
    try:
        with open(COUNTER_FILE) as f:
            return int(f.read().strip())
    except:
        return 0

def set_count(n):
    with open(COUNTER_FILE, "w") as f:
        f.write(str(n))

def load_file(path):
    try:
        with open(path) as f:
            return f.read()
    except:
        return ""

def main():
    data = json.load(sys.stdin)
    count = get_count() + 1
    set_count(count)

    if count % INJECT_EVERY == 0:
        claude_md = load_file(CLAUDE_MD_PATH)
        reminder = ""
        if claude_md:
            reminder += f"[CLAUDE.md REMINDER]\n{claude_md}\n[END REMINDER]\n\n"
        if reminder:
            prompt = data.get("prompt", "")
            data["prompt"] = reminder + prompt

    print(json.dumps(data))

if __name__ == "__main__":
    main()
