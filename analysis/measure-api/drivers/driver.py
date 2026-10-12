# Steps one {grammar, input, chunks} case through the `gbnf` on PYTHONPATH and prints the steps.
# Stdlib only: it runs in whatever interpreter loads the implementation.
import json
import sys

case = json.load(sys.stdin)
stdout, sys.stdout = sys.stdout, sys.stderr

from gbnf import GBNF  # noqa: E402


def observe(label, call):
    try:
        state = call()
        rules = [{"type": type(rule).__name__, "value": getattr(rule, "value", None)} for rule in state]
        return state, {"step": label, "rules": rules}
    except Exception as e:
        pos = getattr(e, "pos", None)
        return None, {"step": label, "error": {"class": type(e).__name__, "pos": pos if type(pos) is int else None}}


start, step = observe("construct", lambda: GBNF(case["grammar"]))
steps = [step]
if start is not None:
    steps.append(observe("whole", lambda: start.add(case["input"]))[1])
    state = start
    for length, chunk in enumerate(case["chunks"], 1):
        state, step = observe(f"prefix {length}", lambda: state.add(chunk))
        steps.append(step)
        if state is None:
            break

stdout.write(json.dumps(steps, ensure_ascii=False, default=repr))
