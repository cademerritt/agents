---
name: speak
description: Speak text aloud using espeak-ng on Linux. Use this skill whenever the user says "speak", "say", "read aloud", "read this out", "voice this", or wants Claude to narrate something. Also use when the user wants a response spoken rather than just displayed. Make sure to use this skill any time audio output or text-to-speech is requested.
argument-hint: text to speak
allowed-tools: Bash(espeak-ng:*)
---

# Speak

Speak text aloud using espeak-ng.

## Steps

1. Take the input text from $ARGUMENTS
2. Run espeak-ng to speak it:

```bash
espeak-ng "$ARGUMENTS"
```

3. If no arguments provided and user wants the last response spoken, ask what text to speak.

## Options

Adjust voice and speed if user requests:

- Slower: `espeak-ng -s 120 "$ARGUMENTS"` (default is ~175 words/min)
- Faster: `espeak-ng -s 220 "$ARGUMENTS"`
- Different voice: `espeak-ng -v en-us "$ARGUMENTS"`

## Examples

User says "speak hello world"
→ Run: `espeak-ng "hello world"`

User says "read this out loud: the file was saved successfully"
→ Run: `espeak-ng "the file was saved successfully"`

User says "say that slower"
→ Run: `espeak-ng -s 120 "[last text]"`
