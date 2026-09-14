"""Record a parse-state trace from the python reference implementation.

For every grammar under tests/iteration/grammars, every test case is replayed
one character at a time and the set of rules the parser will accept next is
recorded after each character. tests/differential.test.ts replays the same
cases against the TypeScript port and asserts the traces match.

Rules are recorded as a *sorted* list of serialized rules. The reference yields
rules in an order derived from python `set` iteration over graph nodes, which
is keyed on object identity and therefore varies between runs -- the accepted
rule set is the meaningful contract, not its order.

Usage:
    python3 tools/record-reference-trace.py tests/fixtures/reference-trace.json
"""

import json
import sys
from pathlib import Path

REFERENCE = Path("/workspace/reference_implementation")
GRAMMARS = Path(__file__).resolve().parent.parent / "tests" / "iteration" / "grammars"

sys.path.insert(0, str(REFERENCE))

from gbnf import GBNF  # noqa: E402

# the reference names rules after their python class; the port uses the same
# type names the test fixtures use.
TYPES = {
    "RuleChar": "char",
    "RuleCharExclude": "char_exclude",
    "RuleEnd": "end",
}


def snapshot(state) -> list[str]:
    rules = []
    for rule in state:
        as_dict = dict(rule.__dict__)
        as_dict["type"] = TYPES[as_dict["type"]]
        rules.append(json.dumps(as_dict, sort_keys=True, separators=(",", ":")))
    return sorted(rules)


def main(destination: str) -> None:
    out = {}
    for grammar_path in sorted(GRAMMARS.glob("*.gbnf")):
        grammar = grammar_path.read_text()
        cases = json.loads(grammar_path.with_suffix(".json").read_text())
        traces = []
        for case in cases:
            state = GBNF(grammar)
            trace = [snapshot(state)]
            for char in case:
                state = state.add(char)
                trace.append(snapshot(state))
            traces.append(trace)
        out[grammar_path.stem] = traces

    Path(destination).write_text(json.dumps(out, separators=(",", ":")) + "\n")
    print(f"wrote {destination}")


if __name__ == "__main__":
    main(sys.argv[1])
