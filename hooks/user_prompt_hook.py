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

def load_claude_md():
    try:
        with open(CLAUDE_MD_PATH) as f:
            return f.read()
    except:
        return ""

def main():
    data = json.load(sys.stdin)
    count = get_count() + 1
    set_count(count)

    if count % INJECT_EVERY == 0:
        claude_md = load_claude_md()
        if claude_md:
            prompt = data.get("prompt", "")
            data["prompt"] = f"[CLAUDE.md REMINDER]\n{claude_md}\n[END REMINDER]\n\n{prompt}"

    print(json.dumps(data))

if __name__ == "__main__":
    main()
