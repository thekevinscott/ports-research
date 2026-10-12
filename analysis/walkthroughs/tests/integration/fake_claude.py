#!/usr/bin/env python3
"""A stand-in for the claude CLI: logs each call and answers with the walkthrough in FAKE_CLAUDE_WALKTHROUGH."""

import json
import os
import sys

argv = sys.argv[1:]
prompt = sys.stdin.read()
with open(os.environ["FAKE_CLAUDE_LOG"], "a") as log:
    log.write(json.dumps({"argv": argv, "cwd": os.getcwd(), "api_key": "ANTHROPIC_API_KEY" in os.environ, "prompt": prompt}) + "\n")
walkthrough = json.loads(os.environ["FAKE_CLAUDE_WALKTHROUGH"])
print(json.dumps({
    "type": "result",
    "is_error": False,
    "result": json.dumps(walkthrough),
    "structured_output": walkthrough,
    "usage": {"input_tokens": len(prompt) // 4, "output_tokens": 100},
}))
