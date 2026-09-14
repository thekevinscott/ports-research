import json
import os
import subprocess
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def run_cli(*args):
    return subprocess.run(
        ["uv", "run", "measure-ast", *args],
        cwd=PACKAGE_ROOT,
        env=os.environ,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def python_tree(tmp_path: Path) -> Path:
    root = tmp_path.resolve()
    (root / "pkg").mkdir()
    (root / "pkg" / "a.py").write_bytes(b"def f(a):\n    if a:\n        return 1\n    return 2\n")
    (root / "pkg" / "b.py").write_bytes(b"x = 1\n")
    (root / "pkg" / "a_test.py").write_bytes(b"def g():\n    return 1\n")
    (root / "pkg" / "notes.md").write_text("not code")
    (root / "build").mkdir()
    (root / "build" / "c.py").write_bytes(b"def h():\n    return 1\n")
    return root


@pytest.fixture
def typescript_tree(tmp_path: Path) -> Path:
    root = tmp_path.resolve()
    (root / "src").mkdir()
    (root / "src" / "a.ts").write_bytes(b"export function f(a: boolean) {\n  return a ? 1 : 2;\n}\n")
    (root / "src" / "b.tsx").write_bytes(b"const y = 1;\n")
    (root / "src" / "a.test.ts").write_bytes(b"const t = 1;\n")
    (root / "node_modules" / "x").mkdir(parents=True)
    (root / "node_modules" / "x" / "c.ts").write_bytes(b"function h() {}\n")
    return root


def describe_measure_ast():
    def it_reports_exact_metrics_for_a_python_tree(python_tree):
        result = run_cli(
            "--language", "python", "--target", str(python_tree),
            "--exclude", "*_test.py", "--exclude", "build",
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout) == {
            "language": "python",
            "target": str(python_tree),
            "parsed_file_count": 2,
            "node_count": 18,
            "max_depth": 6,
            "function_count": 1,
            "mean_function_lines": 4.0,
            "max_function_lines": 4,
            "mean_cyclomatic": 2.0,
            "max_cyclomatic": 2,
        }

    def it_reports_exact_metrics_for_a_typescript_tree(typescript_tree):
        result = run_cli(
            "--language", "typescript", "--target", str(typescript_tree),
            "--exclude", "*.test.ts", "--exclude", "node_modules",
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout) == {
            "language": "typescript",
            "target": str(typescript_tree),
            "parsed_file_count": 2,
            "node_count": 20,
            "max_depth": 6,
            "function_count": 1,
            "mean_function_lines": 3.0,
            "max_function_lines": 3,
            "mean_cyclomatic": 2.0,
            "max_cyclomatic": 2,
        }

    def it_fails_with_a_message_when_the_target_does_not_exist(tmp_path):
        result = run_cli("--language", "python", "--target", str(tmp_path / "nowhere"))
        assert result.returncode != 0
        assert result.stdout == ""
        assert "nowhere" in result.stderr

    def it_fails_with_a_message_when_no_file_parses(tmp_path):
        (tmp_path / "notes.md").write_text("not code")
        result = run_cli("--language", "typescript", "--target", str(tmp_path))
        assert result.returncode != 0
        assert result.stdout == ""
        assert "no typescript source" in result.stderr
