import json
import os
import subprocess
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def run_cli(*args):
    return subprocess.run(
        ["uv", "run", "measure-code-distance", "levenshtein", *args],
        cwd=PACKAGE_ROOT,
        env=os.environ,
        capture_output=True,
        text=True,
    )


def write_tree(root: Path, files: dict[str, str]) -> Path:
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


@pytest.fixture
def python_pair(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path.resolve()
    a = write_tree(
        root / "a",
        {
            "pkg/m.py": "def f(a):\n    return a + 1\n",
            "pkg/m_test.py": "def test_f():\n    assert f(1) == 2\n",
            "build/junk.py": "x = 1\n",
        },
    )
    b = write_tree(
        root / "b",
        {
            "pkg/m.py": "def g(b):\n    return b + 2\n",
            "pkg/notes.md": "not code",
        },
    )
    return a, b


@pytest.fixture
def typescript_pair(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path.resolve()
    a = write_tree(
        root / "a",
        {
            "src/m.ts": "export const f = (a: number) => a + 1;\n",
            "src/m.test.ts": "f(1);\n",
            "node_modules/x/c.ts": "function h() {}\n",
        },
    )
    b = write_tree(root / "b", {"src/m.ts": "export const g = (b: number) => b + 1;\n"})
    return a, b


def describe_measure_code_distance():
    def it_reports_exact_distances_for_a_python_pair(python_pair):
        a, b = python_pair
        result = run_cli(
            "--language", "python", "--a", str(a), "--b", str(b),
            "--exclude", "*_test.py", "--exclude", "build",
        )
        assert result.returncode == 0, result.stderr
        report = json.loads(result.stdout)
        assert report == {
            "language": "python",
            "a": str(a),
            "b": str(b),
            "file_count_a": 1,
            "file_count_b": 1,
            "token_count_a": 10,
            "token_count_b": 10,
            "char_count_a": 27,
            "char_count_b": 27,
            "token_levenshtein": pytest.approx(1 / 10),
            "token_levenshtein_raw": pytest.approx(4 / 10),
            "char_levenshtein": pytest.approx(4 / 27),
            "path_count_a": 1,
            "path_count_b": 2,
            "path_levenshtein": pytest.approx(1 / 2),
        }

    def it_reports_exact_distances_for_a_typescript_pair(typescript_pair):
        a, b = typescript_pair
        result = run_cli(
            "--language", "typescript", "--a", str(a), "--b", str(b),
            "--exclude", "*.test.ts", "--exclude", "node_modules",
        )
        assert result.returncode == 0, result.stderr
        report = json.loads(result.stdout)
        assert (report["file_count_a"], report["file_count_b"]) == (1, 1)
        assert report["token_levenshtein"] == 0.0
        assert report["token_levenshtein_raw"] == pytest.approx(3 / 14)
        assert report["char_levenshtein"] == pytest.approx(3 / 39)

    def it_is_zero_for_a_codebase_against_itself(python_pair):
        a, _ = python_pair
        result = run_cli("--language", "python", "--a", str(a), "--b", str(a))
        assert result.returncode == 0, result.stderr
        report = json.loads(result.stdout)
        assert (report["token_levenshtein"], report["token_levenshtein_raw"], report["char_levenshtein"]) == (0.0, 0.0, 0.0)
        assert (report["file_count_a"], report["file_count_b"]) == (3, 3)

    def it_fails_with_a_message_when_a_directory_does_not_exist(python_pair, tmp_path):
        a, _ = python_pair
        result = run_cli("--language", "python", "--a", str(a), "--b", str(tmp_path / "nowhere"))
        assert result.returncode != 0
        assert result.stdout == ""
        assert "nowhere" in result.stderr

    def it_fails_with_a_message_when_a_side_has_no_source(python_pair, tmp_path):
        a, _ = python_pair
        empty = tmp_path / "empty"
        empty.mkdir()
        (empty / "notes.md").write_text("not code")
        result = run_cli("--language", "python", "--a", str(a), "--b", str(empty))
        assert result.returncode != 0
        assert result.stdout == ""
        assert "no python source" in result.stderr
