"""Runs the corpus through the ported implementation. Invoked by run.py."""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, ".work")
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

from gbnf import GBNF, GrammarParseError, InputParseError  # noqa: E402
from gbnf.grammar_graph.types import RuleEnd  # noqa: E402


def describe_error(err: BaseException) -> dict:
    if isinstance(err, GrammarParseError):
        name = "GrammarParseError"
    elif isinstance(err, InputParseError):
        name = "InputParseError"
    else:
        name = "Error"
    return {"error": name, "message": str(err)}


def rules_of(state) -> list:
    rules = []
    for rule in state:
        if isinstance(rule, RuleEnd):
            rules.append({"type": rule.type.value})
        else:
            rules.append({"type": rule.type.value, "value": rule.value})
    return rules


def main() -> None:
    with open(os.path.join(WORK, "corpus.json"), encoding="utf-8") as fh:
        cases = json.load(fh)

    results = []
    for case in cases:
        grammar, inputs = case["grammar"], case["inputs"]
        trace = {"grammar": grammar, "construct": None, "adds": []}
        try:
            state = GBNF(grammar)
            trace["construct"] = {"rules": rules_of(state)}
        except Exception as err:  # noqa: BLE001 - mirrors the JavaScript harness
            trace["construct"] = describe_error(err)
            results.append(trace)
            continue

        for input_ in inputs:
            entry = {"input": input_, "whole": None, "incremental": None}
            # the whole input applied to the state built above...
            try:
                entry["whole"] = {"rules": rules_of(state.add(input_))}
            except Exception as err:  # noqa: BLE001
                entry["whole"] = describe_error(err)
            # ...and the same input applied one character at a time to a fresh state
            try:
                cursor = GBNF(grammar)
                for char in input_:
                    cursor = cursor.add(char)
                entry["incremental"] = {"rules": rules_of(cursor)}
            except Exception as err:  # noqa: BLE001
                entry["incremental"] = describe_error(err)
            trace["adds"].append(entry)
        results.append(trace)

    with open(os.path.join(WORK, "out-py.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1)
    print(f"port: wrote {len(results)} traces")


if __name__ == "__main__":
    main()
