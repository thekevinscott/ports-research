# Runs one {grammar, input} pair through the `gbnf` under argv[1] and prints {outcome, error}.
# Stdlib only: it runs in whatever interpreter loads the implementation.
import json
import sys

sys.path.insert(0, sys.argv[1])
pair = json.load(sys.stdin)
stdout, sys.stdout = sys.stdout, sys.stderr

from gbnf import GBNF, RuleEnd  # noqa: E402

try:
    state = GBNF(pair["grammar"], pair["input"])
    outcome, error = ("accept" if any(isinstance(rule, RuleEnd) for rule in state) else "reject"), None
except Exception as e:
    outcome = "reject" if type(e).__name__ == "InputParseError" else "error"
    error = f"{type(e).__name__}: {e}"

stdout.write(json.dumps({"outcome": outcome, "error": error}))
