"""A pytest plugin that records every build_rule_stack call the reference suite makes.

Run from the reference implementation's root:

    uv run --offline --no-project --with pytest==9.1.1 --with pytest-describe==3.2.0 \
        python -m pytest gbnf/grammar_parser/build_rule_stack_test.py \
        -p record_build_rule_stack

with this file importable as `record_build_rule_stack` and `GBNF_RECORD_OUT` pointing
at the fixture to write. The plugin patches the function before pytest imports the
test module, so the test module's `from .build_rule_stack import build_rule_stack`
binding picks up the recorder.
"""

from __future__ import annotations

import atexit
import json
import os
from pathlib import Path

import gbnf.grammar_parser.build_rule_stack as module

OUT = Path(os.environ.get("GBNF_RECORD_OUT", "build_rule_stack_test.json"))

_records: list[dict] = []
_seen: set[str] = set()
_original = module.build_rule_stack


def _encode(obj):
    if isinstance(obj, (list, tuple)):
        return [_encode(item) for item in obj]
    if isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    name = type(obj).__name__
    if hasattr(obj, "value"):
        return {"cls": name, "value": _encode(obj.value)}
    return {"cls": name}


def _recording_build_rule_stack(linear_rules):
    encoded_input = _encode(linear_rules)
    result = _original(linear_rules)
    record = {"input": encoded_input, "expected": _encode(result)}
    key = json.dumps(record, sort_keys=True)
    if key not in _seen:
        _seen.add(key)
        _records.append(record)
    return result


module.build_rule_stack = _recording_build_rule_stack


@atexit.register
def _dump() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(_records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nrecorded {len(_records)} build_rule_stack case(s) to {OUT}")
