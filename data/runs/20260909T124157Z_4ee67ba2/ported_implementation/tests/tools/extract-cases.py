#!/usr/bin/env python3
"""Extract the pytest parametrize tables from /workspace/tests/python into JSON.

The ported test suite is a TypeScript translation of the Python suite; the *cases*
are pulled straight out of the Python source rather than retyped, so the two suites
provably exercise the same inputs.

Usage:
    python3 tests/tools/extract-cases.py [PYTHON_TESTS_DIR] [OUT_DIR]
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

DEFAULT_SRC = Path("/workspace/tests/python")
DEFAULT_OUT = Path(__file__).resolve().parent.parent / "fixtures"

# Names the parametrize tables are allowed to reference.
EVAL_GLOBALS = {"ord": ord, "chr": chr}


def parametrize_tables(path: Path) -> dict[str, dict]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    tables: dict[str, dict] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            func = decorator.func
            if not (isinstance(func, ast.Attribute) and func.attr == "parametrize"):
                continue
            try:
                argnames = eval(ast.unparse(decorator.args[0]), EVAL_GLOBALS)  # noqa: S307
                argvalues = eval(ast.unparse(decorator.args[1]), EVAL_GLOBALS)  # noqa: S307
            except NameError as err:
                # Tables built at runtime (e.g. grammars_test loads its cases from
                # disk) are reproduced directly by the TypeScript suite instead.
                print(f"skipping {path.name}::{node.name}: {err}")
                continue
            if isinstance(argnames, str):
                argnames = [n.strip() for n in argnames.split(",")]
                cases = [[v] for v in argvalues] if len(argnames) == 1 else argvalues
            else:
                argnames = list(argnames)
                cases = argvalues
            tables[node.name] = {
                "argnames": argnames,
                "cases": [list(case) for case in cases],
            }
    return tables


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT
    out.mkdir(parents=True, exist_ok=True)

    total = 0
    for test_file in sorted(src.rglob("*_test.py")):
        tables = parametrize_tables(test_file)
        if not tables:
            continue
        target = out / f"{test_file.stem}.json"
        target.write_text(json.dumps(tables, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        count = sum(len(t["cases"]) for t in tables.values())
        total += count
        print(f"{target.name}: {len(tables)} table(s), {count} case(s)")
    print(f"total cases: {total}")


if __name__ == "__main__":
    main()
