"""Assert the port matches the reference implementation on the shared corpus.

The expected values in ``fixtures/reference.json`` were produced by running
``reference_implementation`` itself (see ``tools/record_reference.py``).
"""

from __future__ import annotations

import json
import pathlib
import sys
import unittest
from typing import Any, Dict, List

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from cases import CASES  # noqa: E402

from ported_implementation import GBNF, GrammarParseError, InputParseError  # noqa: E402

FIXTURE = json.loads((HERE / "fixtures" / "reference.json").read_text())
BY_NAME: Dict[str, Dict[str, Any]] = {case["name"]: case for case in FIXTURE}

# Python raises RecursionError where the reference raises a Javascript RangeError.
STACK_OVERFLOW = "stack-overflow"


def serialize(rule: Any) -> Dict[str, Any]:
    if rule.type == "end":
        return {"type": rule.type.value}
    return {"type": rule.type.value, "value": rule.value}


def run_case(case: Dict[str, Any]) -> Dict[str, Any]:
    try:
        state = GBNF(case["grammar"], case.get("initial", ""))
        steps: List[List[Dict[str, Any]]] = [[serialize(rule) for rule in state]]
        for chunk in case.get("adds", []):
            state = state.add(chunk)
            steps.append([serialize(rule) for rule in state])
        return {
            "name": case["name"],
            "ok": True,
            "steps": steps,
            "size": state.size,
            "grammar": state.grammar,
        }
    except (GrammarParseError, InputParseError) as err:
        return {
            "name": case["name"],
            "ok": False,
            "error": type(err).__name__,
            "message": str(err),
        }
    except RecursionError:
        # The reference exhausts the Javascript call stack on the same grammars.
        return {"name": case["name"], "ok": False, "error": STACK_OVERFLOW}


def normalize(result: Dict[str, Any]) -> Dict[str, Any]:
    """Collapse the two runtimes' distinct stack-overflow reports onto one value."""
    if result.get("error") in ("RangeError", STACK_OVERFLOW):
        return {"name": result["name"], "ok": False, "error": STACK_OVERFLOW}
    return result


class ParityTest(unittest.TestCase):
    def test_every_case_is_recorded(self) -> None:
        self.assertEqual([case["name"] for case in CASES], [case["name"] for case in FIXTURE])


def _add_case(case: Dict[str, Any]) -> None:
    def test(self: ParityTest) -> None:
        expected = BY_NAME[case["name"]]
        self.assertEqual(normalize(run_case(case)), normalize(expected))

    test.__name__ = f"test_{case['name'].replace('-', '_')}"
    test.__doc__ = f"{case['name']}: matches the reference implementation"
    setattr(ParityTest, test.__name__, test)


for _case in CASES:
    _add_case(_case)


if __name__ == "__main__":
    unittest.main()
