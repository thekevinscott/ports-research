"""Record the exact error strings the python reference implementation renders.

The translated error tests build their expectation with the port's own error
classes, so they would pass even if the rendered message drifted from the
reference. This records the reference's `str(error)` for every error case in
the suite; tests/error-messages.test.ts asserts the port renders the same text.

Usage:
    python3 tools/record-reference-errors.py tests/fixtures/reference-errors.json
"""

import json
import sys
from pathlib import Path

REFERENCE = Path("/workspace/reference_implementation")
FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"

sys.path.insert(0, str(REFERENCE))

from gbnf import GBNF, GrammarParseError, InputParseError  # noqa: E402


def load(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.json").read_text())


def main(destination: str) -> None:
    out: dict[str, list] = {"grammar": [], "input": []}

    cases = load("validate_grammar_test")
    for grammar, _pos, _reason in cases[
        "test_it_reports_an_error_for_an_invalid_grammar"
    ]["argvalues"]:
        try:
            GBNF(grammar)
        except GrammarParseError as err:
            out["grammar"].append({"grammar": grammar, "message": str(err)})
        else:
            raise AssertionError(f"expected a GrammarParseError for {grammar!r}")

    cases = load("validate_input_test")
    for grammar, input_text, _pos in cases[
        "test_it_reports_an_error_for_an_invalid_input"
    ]["argvalues"]:
        graph = GBNF(grammar)
        try:
            graph.add(input_text)
        except InputParseError as err:
            out["input"].append(
                {
                    "grammar": grammar,
                    "input": input_text,
                    "message": str(err),
                    "errorForMostRecentInput": err.error_for_most_recent_input,
                    "src": err.src,
                },
            )
        else:
            raise AssertionError(f"expected an InputParseError for {input_text!r}")

    # the incremental case from iteration_with_additional_strings_test
    state = GBNF('root ::= "bar"').add("b").add("a")
    try:
        state.add("z")
    except InputParseError as err:
        out["incremental"] = {
            "message": str(err),
            "errorForMostRecentInput": err.error_for_most_recent_input,
            "src": err.src,
        }
    else:
        raise AssertionError("expected an InputParseError")

    Path(destination).write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {destination}")


if __name__ == "__main__":
    main(sys.argv[1])
