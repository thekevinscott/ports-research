"""Run the corpus through the Python port, producing the same JSON shape as
``run_reference.ts`` so the two can be compared directly."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gbnf import GBNF  # noqa: E402
from gbnf.grammar_graph.parse_state import ParseState  # noqa: E402


def describe_error(e: BaseException) -> Dict[str, Any]:
    return {"ok": False, "error": type(e).__name__, "message": str(e)}


def describe_state(state: ParseState) -> Dict[str, Any]:
    return {
        "ok": True,
        "rules": [rule.to_dict() for rule in state],
        "size": state.size,
        "grammar": state.grammar,
        "graph": state._graph.print(pointers=state._pointers, colors=False),
        "graphColored": state._graph.print(pointers=state._pointers, colors=True),
    }


def run(corpus: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for test_case in corpus:
        entry: Dict[str, Any] = {"name": test_case["name"]}

        if "inputs" in test_case:
            inputs = []
            for input in test_case["inputs"]:
                try:
                    inputs.append(describe_state(GBNF(test_case["grammar"], input)))
                except Exception as e:  # noqa: BLE001 - mirroring `catch (e)`
                    inputs.append(describe_error(e))
            entry["inputs"] = inputs

        if "code_point_inputs" in test_case:
            code_point_inputs = []
            for input in test_case["code_point_inputs"]:
                try:
                    code_point_inputs.append(
                        describe_state(GBNF(test_case["grammar"], input))
                    )
                except Exception as e:  # noqa: BLE001
                    code_point_inputs.append(describe_error(e))
            entry["code_point_inputs"] = code_point_inputs

        if "steps" in test_case:
            step_results: List[Dict[str, Any]] = []
            try:
                state = GBNF(test_case["grammar"])
                step_results.append(describe_state(state))
                for step in test_case["steps"]:
                    try:
                        state = state.add(step)
                        step_results.append(describe_state(state))
                    except Exception as e:  # noqa: BLE001
                        step_results.append(describe_error(e))
                        break
            except Exception as e:  # noqa: BLE001
                step_results.append(describe_error(e))
            entry["steps"] = step_results

        results.append(entry)
    return results


if __name__ == "__main__":
    corpus_path = Path(sys.argv[1])
    print(json.dumps(run(json.loads(corpus_path.read_text())), indent=2))
