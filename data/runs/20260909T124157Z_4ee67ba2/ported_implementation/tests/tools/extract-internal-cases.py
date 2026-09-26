#!/usr/bin/env python3
"""Extract the data-heavy tables from the reference implementation's own unit tests.

Two tables are far too large to retype by hand:

  * `rules_builder_test.test_cases` - a module-level list, read straight out of the
    source with `ast` + `eval` and serialized to JSON.
  * `build_rule_stack_test` - inputs are spread across inline asserts, locals and
    parametrize tables. Rather than scrape each shape, the reference suite is run
    with `build_rule_stack` wrapped in a recorder (see `record-build-rule-stack.py`),
    capturing every (input, output) pair the reference tests assert on.

Usage:
    python3 tests/tools/extract-internal-cases.py [REFERENCE_DIR] [OUT_DIR]
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

DEFAULT_REF = Path("/workspace/reference_implementation")
DEFAULT_OUT = Path(__file__).resolve().parent.parent / "fixtures"


def encode(obj):
    """Serialize reference rule objects to `{cls, value}` tags the TS suite can rebuild."""
    if isinstance(obj, (list, tuple)):
        return [encode(item) for item in obj]
    if isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    name = type(obj).__name__
    if hasattr(obj, "value"):
        return {"cls": name, "value": encode(obj.value)}
    return {"cls": name}


def extract_rules_builder_cases(ref: Path) -> list[dict]:
    source = (ref / "gbnf/rules_builder/rules_builder_test.py").read_text(encoding="utf-8")
    sys.path.insert(0, str(ref))
    from gbnf.rules_builder import rules_builder_types as t  # noqa: PLC0415

    namespace = {
        "ord": ord,
        "chr": chr,
        **{name: getattr(t, name) for name in dir(t) if name.startswith("InternalRuleDef")},
    }

    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "test_cases"
            for target in node.targets
        ):
            raw = eval(ast.unparse(node.value), namespace)  # noqa: S307
            return [
                {
                    "key": key,
                    "grammar": grammar,
                    "symbolIds": [list(pair) for pair in expected[0]],
                    "rules": encode(expected[1]),
                }
                for key, grammar, expected in raw
            ]
    raise RuntimeError("Could not find `test_cases` in rules_builder_test.py")


def main() -> None:
    ref = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_REF
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT
    out.mkdir(parents=True, exist_ok=True)

    cases = extract_rules_builder_cases(ref)
    target = out / "rules_builder_test.json"
    target.write_text(json.dumps(cases, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{target.name}: {len(cases)} case(s)")


if __name__ == "__main__":
    main()
