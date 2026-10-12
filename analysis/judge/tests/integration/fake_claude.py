#!/usr/bin/env python3
"""A stand-in for the claude CLI: logs each call and answers with canned verdicts that fit the schema."""

import json
import os
import sys

argv = sys.argv[1:]
prompt = sys.stdin.read()
with open(os.environ["FAKE_CLAUDE_LOG"], "a") as log:
    log.write(json.dumps({"argv": argv, "cwd": os.getcwd(), "api_key": "ANTHROPIC_API_KEY" in os.environ, "prompt": prompt}) + "\n")
if os.environ.get("FAKE_CLAUDE_FAIL"):
    print("rate limited", file=sys.stderr)
    sys.exit(1)

schema = json.loads(argv[argv.index("--json-schema") + 1])
if "cheating" in schema["properties"]:
    verdicts = {
        "cheating": {"verdict": ["none"], "evidence": [], "confidence": "unsure"},
        "shipped_material_read": {"verdict": ["source"], "evidence": [{"position": 2, "quote": "ls /input"}], "confidence": "sure"},
        "tests_run": {"verdict": ["none"], "evidence": [], "confidence": "sure"},
        "own_tests": {"verdict": ["none"], "evidence": [], "confidence": "likely"},
        "structure": {"verdict": "kept", "evidence": [], "confidence": "sure", "rationale": "not stated"},
    }
else:
    item = {"evidence": [{"side": "A", "file": "gbnf/GBNF.py", "lines": "1", "quote": "x"}], "note": "n"}
    verdicts = {
        "api_parity": {"verdict": "complete", **item},
        "structure": {"verdict": "kept", **item},
        "semantic_divergences": {"verdict": "none-found", "divergences": [], **item},
        "idiom": {"verdict": "mixed", **item},
        "dropped_or_added": {"verdict": "neither", **item},
        "fidelity": {"verdict": 4, "note": "n"},
    }
print(json.dumps({
    "type": "result",
    "is_error": False,
    "result": json.dumps(verdicts),
    "structured_output": verdicts,
    "usage": {"input_tokens": len(prompt) // 4, "output_tokens": 100},
}))
