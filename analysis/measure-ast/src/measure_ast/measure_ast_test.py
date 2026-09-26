from pathlib import Path

import pytest

from measure_ast.measure_ast import measure_ast

BRANCHING = b"def f(a):\n    if a:\n        return 1\n    return 2\n"
ASSIGNMENT = b"x = 1\n"
PLAIN = b"def g():\n    return 1\n"
EXCLUDE = ["*_test.py", "build"]


@pytest.fixture
def python_tree(tmp_path: Path) -> Path:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "a.py").write_bytes(BRANCHING)
    (tmp_path / "pkg" / "b.py").write_bytes(ASSIGNMENT)
    (tmp_path / "pkg" / "a_test.py").write_bytes(PLAIN)
    (tmp_path / "pkg" / "notes.md").write_text("not code")
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "c.py").write_bytes(PLAIN)
    return tmp_path


@pytest.fixture
def typescript_tree(tmp_path: Path) -> Path:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.ts").write_bytes(b"export const a = 1;\n")
    (tmp_path / "src" / "b.tsx").write_bytes(b"export const b = <div />;\n")
    (tmp_path / "src" / "a.test.ts").write_bytes(b"export const t = 1;\n")
    return tmp_path


def describe_measure_ast():
    def it_reports_the_language_and_target(python_tree):
        report = measure_ast(language="python", target=python_tree, exclude=EXCLUDE)
        assert (report["language"], report["target"]) == ("python", str(python_tree))

    def it_parses_the_files_left_after_exclusion(python_tree):
        assert measure_ast(language="python", target=python_tree, exclude=EXCLUDE)["parsed_file_count"] == 2

    def it_parses_every_python_file_without_excludes(python_tree):
        assert measure_ast(language="python", target=python_tree, exclude=[])["parsed_file_count"] == 4

    def it_sums_node_counts_over_files(python_tree):
        assert measure_ast(language="python", target=python_tree, exclude=EXCLUDE)["node_count"] == 18

    def it_takes_the_deepest_depth_over_files(python_tree):
        assert measure_ast(language="python", target=python_tree, exclude=EXCLUDE)["max_depth"] == 6

    def it_aggregates_functions_over_files(python_tree):
        report = measure_ast(language="python", target=python_tree, exclude=["build"])
        assert report["function_count"] == 2
        assert report["mean_function_lines"] == 3.0
        assert report["max_function_lines"] == 4
        assert report["mean_cyclomatic"] == 1.5
        assert report["max_cyclomatic"] == 2

    def it_reports_zero_means_and_maxes_without_functions(python_tree):
        report = measure_ast(language="python", target=python_tree, exclude=[*EXCLUDE, "a.py"])
        assert report["function_count"] == 0
        assert report["mean_function_lines"] == 0
        assert report["max_function_lines"] == 0
        assert report["mean_cyclomatic"] == 0
        assert report["max_cyclomatic"] == 0

    def it_parses_ts_and_tsx_for_typescript(typescript_tree):
        report = measure_ast(language="typescript", target=typescript_tree, exclude=["*.test.ts"])
        assert report["parsed_file_count"] == 2

    def it_raises_when_no_file_parsed(tmp_path):
        with pytest.raises(FileNotFoundError, match="no python source"):
            measure_ast(language="python", target=tmp_path, exclude=[])
