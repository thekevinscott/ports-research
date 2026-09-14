"""Extract the parametrize data from the generated Python test suite into JSON fixtures.

The TypeScript tests in `tests/` are ports of `/workspace/tests/python`. Their case tables are
pure data, so rather than transcribing thousands of rows by hand (and risking a typo silently
weakening a test), the tables are lifted straight out of the Python sources and written to
`tests/fixtures/*.json`, which the TypeScript tests import.

Usage:

    python3 tests/tools/extract-python-fixtures.py [python-suite-dir]

Defaults to /workspace/tests/python. Re-run it if the Python suite changes.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

DEFAULT_SUITE_DIR = Path("/workspace/tests/python")
OUT_DIR = Path(__file__).resolve().parent.parent / "fixtures"

# The case tables use `ord(...)` to spell out code points; nothing else needs to be callable.
EVAL_GLOBALS = {"ord": ord}


def evaluate(node: ast.expr):
    return eval(compile(ast.Expression(node), "<fixture>", "eval"), dict(EVAL_GLOBALS))


def extract_blocks(path: Path) -> list[dict]:
    tree = ast.parse(path.read_text())
    blocks: list[tuple[int, dict]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if getattr(node.func, "attr", None) != "parametrize" or len(node.args) < 2:
            continue
        argvalues_node = node.args[1]
        if isinstance(argvalues_node, ast.Call):
            # e.g. `_load_cases()`; the TypeScript test reads those fixtures directly.
            continue
        blocks.append(
            (
                node.lineno,
                {
                    "argnames": evaluate(node.args[0]),
                    "argvalues": evaluate(argvalues_node),
                },
            ),
        )
    return [block for _, block in sorted(blocks, key=lambda item: item[0])]


def main() -> None:
    suite_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SUITE_DIR
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(suite_dir.rglob("*_test.py")):
        blocks = extract_blocks(path)
        if not blocks:
            continue
        out_path = OUT_DIR / f"{path.stem.removesuffix('_test').replace('_', '-')}.json"
        out_path.write_text(
            json.dumps(blocks, ensure_ascii=False, indent=2) + "\n",
        )
        print(f"{path} -> {out_path} ({len(blocks)} block(s))")  # noqa: T201


if __name__ == "__main__":
    main()
