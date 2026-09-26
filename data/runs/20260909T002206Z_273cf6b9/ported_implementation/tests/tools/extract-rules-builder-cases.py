"""Extract the `test_cases` table from the reference implementation's rules_builder_test.py.

The table is ~1400 lines of `InternalRuleDef*` literals. Rather than transcribing it by hand,
it is evaluated with stub constructors that emit plain dicts, and written to
`tests/fixtures/rules-builder.json` for the TypeScript port of the test to rebuild.

Usage:

    python3 tests/tools/extract-rules-builder-cases.py [path-to-rules_builder_test.py]
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

DEFAULT_SOURCE = Path(
    "/workspace/reference_implementation/gbnf/rules_builder/rules_builder_test.py",
)
OUT_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "rules-builder.json"


def stub(kind: str):
    def build(value=None):
        if value is None:
            return {"kind": kind}
        return {"kind": kind, "value": value}

    return build


EVAL_GLOBALS = {
    "ord": ord,
    "InternalRuleDefChar": stub("char"),
    "InternalRuleDefCharAlt": stub("char_alt"),
    "InternalRuleDefCharNot": stub("char_not"),
    "InternalRuleDefCharRngUpper": stub("char_rng_upper"),
    "InternalRuleDefReference": stub("ref"),
    "InternalRuleDefAlt": stub("alt"),
    "InternalRuleDefEnd": stub("end"),
}


def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SOURCE
    tree = ast.parse(source.read_text())
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and getattr(node.targets[0], "id", None) == "test_cases"
        ):
            cases = eval(  # noqa: S307
                compile(ast.Expression(node.value), "<fixture>", "eval"),
                dict(EVAL_GLOBALS),
            )
            OUT_PATH.write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n")
            print(f"{source} -> {OUT_PATH} ({len(cases)} case(s))")  # noqa: T201
            return
    raise SystemExit("Could not find a `test_cases` assignment")


if __name__ == "__main__":
    main()
