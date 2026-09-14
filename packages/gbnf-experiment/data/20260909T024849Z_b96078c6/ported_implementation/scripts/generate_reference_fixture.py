"""Generate golden fixtures from the Python reference implementation.

Run from the repository root:

    python3 ported_implementation/scripts/generate_reference_fixture.py

The fixtures are consumed by ported_implementation/test/differential.test.ts, which
asserts that the TypeScript port produces byte-identical results.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "reference_implementation"))

from gbnf import GBNF  # noqa: E402
from gbnf.grammar_graph.grammar_graph_types import (  # noqa: E402
    RuleChar,
    RuleCharExclude,
    RuleEnd,
)
from gbnf.grammar_graph.rule_ref import RuleRef  # noqa: E402
from gbnf.grammar_parser.build_rule_stack import build_rule_stack  # noqa: E402
from gbnf.rules_builder import RulesBuilder  # noqa: E402
from gbnf.utils.errors import GrammarParseError, InputParseError  # noqa: E402


def ser_internal(rule) -> dict:
    name = type(rule).__name__
    if hasattr(rule, "value"):
        return {"type": name, "value": rule.value}
    return {"type": name}


def ser_rule(rule) -> dict:
    if isinstance(rule, RuleEnd):
        return {"type": "RuleEnd"}
    if isinstance(rule, RuleChar):
        return {"type": "RuleChar", "value": rule.value}
    if isinstance(rule, RuleCharExclude):
        return {"type": "RuleCharExclude", "value": rule.value}
    if isinstance(rule, RuleRef):
        return {"type": "RuleRef", "value": rule.value}
    raise ValueError(f"unknown rule {rule}")


def build(grammar: str) -> dict:
    try:
        builder = RulesBuilder(grammar)
    except GrammarParseError as err:
        return {"error": str(err)}
    rules = [[ser_internal(rule) for rule in rule_list] for rule_list in builder.rules]
    symbol_ids = [[key, value] for key, value in builder.symbol_ids.items()]
    stacks = [
        [[ser_rule(rule) for rule in path] for path in build_rule_stack(rule_list)]
        for rule_list in builder.rules
    ]
    return {"rules": rules, "symbolIds": symbol_ids, "stacks": stacks}


def parse(grammar: str, inputs: list[str]) -> dict:
    steps: list[dict] = []
    try:
        state = GBNF(grammar)
    except (GrammarParseError, InputParseError) as err:
        return {"error": str(err), "steps": steps}
    steps.append({"input": None, "rules": sorted(json.dumps(ser_rule(r), sort_keys=True) for r in state)})
    for text in inputs:
        try:
            state = state.add(text)
        except (GrammarParseError, InputParseError) as err:
            steps.append({"input": text, "error": str(err)})
            break
        steps.append(
            {
                "input": text,
                "rules": sorted(json.dumps(ser_rule(r), sort_keys=True) for r in state),
            },
        )
    return {"steps": steps}


def invalid(grammar: str) -> dict:
    try:
        GBNF(grammar)
    except Exception as err:  # noqa: BLE001 - we want to record whatever comes out
        return {"errorType": type(err).__name__, "error": str(err)}
    return {"errorType": None, "error": None}


def main() -> None:
    grammars = json.loads((HERE / "grammars.json").read_text())
    inputs = json.loads((HERE / "inputs.json").read_text())
    invalid_grammars = json.loads((HERE / "invalid-grammars.json").read_text())

    fixture = {
        "build": [{"key": key, "grammar": grammar, **build(grammar)} for key, grammar in grammars],
        "parse": [],
        "invalid": [
            {"key": key, "grammar": grammar, **invalid(grammar)}
            for key, grammar in invalid_grammars
        ],
    }

    by_key = dict(grammars)
    for key, texts in inputs:
        fixture["parse"].append(
            {"key": key, "grammar": by_key[key], "inputs": texts, **parse(by_key[key], texts)},
        )

    out = HERE.parent / "test" / "fixtures" / "reference.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(fixture, ensure_ascii=False, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
