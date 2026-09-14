import json
import os
import subprocess
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
COUNTS = ("identical", "modified", "renamed", "added", "deleted")


def run_cli(*args):
    return subprocess.run(
        ["uv", "run", "measure-code-distance", "git-diff", *args],
        cwd=PACKAGE_ROOT,
        env=os.environ,
        capture_output=True,
        text=True,
    )


def measure(a: Path, b: Path, *args, language: str = "python") -> dict:
    result = run_cli("--language", language, "--a", str(a), "--b", str(b), *args)
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def write_tree(root: Path, files: dict[str, str]) -> Path:
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


KEPT = "def kept(a):\n    return a + 1\n"
MOVED = "def moved(value):\n    total = value * 2\n    return total\n"
GONE = "def gone():\n    return None\n"


@pytest.fixture
def reference(tmp_path: Path) -> Path:
    return write_tree(
        tmp_path.resolve() / "a",
        {
            "pkg/kept.py": f"# a comment\n{KEPT}",
            "pkg/moved.py": MOVED,
            "pkg/gone.py": GONE,
            "pkg/kept_test.py": "def test_kept():\n    assert kept(1) == 2\n",
        },
    )


@pytest.fixture
def port(tmp_path: Path, reference: Path) -> Path:
    return write_tree(
        tmp_path.resolve() / "b",
        {
            "pkg/kept.py": KEPT,
            "pkg/renamed.py": MOVED,
            "pkg/kept_test.py": "def test_kept():\n    assert False\n",
        },
    )


def describe_git_diff():
    def it_is_zero_for_a_tree_against_itself(reference):
        report = measure(reference, reference, "--exclude", "*_test.py")
        assert report["diff_ratio"] == 0.0
        assert (report["insertions"], report["deletions"]) == (0, 0)

    def it_calls_every_file_identical_for_a_tree_against_itself(reference):
        report = measure(reference, reference, "--exclude", "*_test.py")
        assert {count: report[count] for count in COUNTS} == {
            "identical": 3,
            "modified": 0,
            "renamed": 0,
            "added": 0,
            "deleted": 0,
        }

    def it_counts_the_reference_lines_of_the_normalized_tree(reference):
        assert measure(reference, reference, "--exclude", "*_test.py")["reference_lines"] == 7

    def it_ignores_a_comment_that_only_one_side_carries(reference, port):
        report = measure(reference, port, "--exclude", "*_test.py")
        assert report["identical"] == 1

    def it_lets_git_match_a_renamed_file(reference, port):
        report = measure(reference, port, "--exclude", "*_test.py")
        assert report["renamed"] == 1
        assert report["added"] == 0

    def it_counts_a_file_only_the_reference_has_as_deleted(reference, port):
        report = measure(reference, port, "--exclude", "*_test.py")
        assert report["deleted"] == 1

    def it_scores_a_tree_against_itself_a_hundred_percent_similar(reference):
        assert measure(reference, reference, "--exclude", "*_test.py")["similarity_pct"] == 100.0

    def it_scores_the_similarity_as_dice_over_both_line_counts(reference, port):
        report = measure(reference, port, "--exclude", "*_test.py")
        shared = report["reference_lines"] - report["deletions"]
        port_lines = shared + report["insertions"]
        assert report["similarity_pct"] == pytest.approx(
            100 * 2 * shared / (report["reference_lines"] + port_lines)
        )
        assert 0 < report["similarity_pct"] < 100

    def it_scores_the_churn_against_the_reference_lines(reference, port):
        report = measure(reference, port, "--exclude", "*_test.py")
        assert report["diff_ratio"] == pytest.approx(
            (report["insertions"] + report["deletions"]) / report["reference_lines"]
        )
        assert report["diff_ratio"] > 0

    def it_honours_the_excludes(reference, port):
        kept = measure(reference, port)
        excluded = measure(reference, port, "--exclude", "*_test.py")
        assert kept["reference_lines"] > excluded["reference_lines"]

    def it_reports_no_formatter_failures_for_code_that_parses(reference, port):
        assert measure(reference, port, "--exclude", "*_test.py")["formatter_failures"] == []

    def it_records_a_file_the_formatter_refuses(reference, port):
        (port / "pkg" / "broken.py").write_text("def (:\n")
        assert measure(reference, port, "--exclude", "*_test.py")["formatter_failures"] == [
            {"side": "b", "path": "pkg/broken.py"}
        ]

    def it_fails_with_a_message_when_a_directory_does_not_exist(reference, tmp_path):
        result = run_cli("--language", "python", "--a", str(reference), "--b", str(tmp_path / "nowhere"))
        assert result.returncode != 0
        assert result.stdout == ""
        assert "nowhere" in result.stderr

    def it_fails_with_a_message_when_a_side_has_no_source(reference, tmp_path):
        empty = write_tree(tmp_path / "empty", {"notes.md": "not code"})
        result = run_cli("--language", "python", "--a", str(reference), "--b", str(empty))
        assert result.returncode != 0
        assert result.stdout == ""
        assert "no python source" in result.stderr

    def it_measures_a_typescript_pair_through_prettier(tmp_path):
        source = "export const f = (a: number) => a + 1;\n"
        a = write_tree(tmp_path.resolve() / "ts-a", {"src/m.ts": "// note\nexport const f = (a:number)=>a+1\n"})
        b = write_tree(tmp_path.resolve() / "ts-b", {"src/m.ts": source})
        report = measure(a, b, language="typescript")
        assert (report["diff_ratio"], report["identical"], report["reference_lines"]) == (0.0, 1, 1)
