from pathlib import Path

import pytest

from round_trip_experiment.collect_files import collect_files


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "a.py").write_text("")
    (tmp_path / "pkg" / "a_test.py").write_text("")
    (tmp_path / "pkg" / "notes.md").write_text("")
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "b.py").write_text("")
    (tmp_path / "top.py").write_text("")
    return tmp_path


def collect(tree, exclude):
    return [p.relative_to(tree).as_posix() for p in collect_files(tree, suffixes={".py"}, exclude=exclude)]


def describe_collect_files():
    def it_returns_files_with_the_given_suffixes_sorted_by_path(tree):
        assert collect(tree, []) == ["build/b.py", "pkg/a.py", "pkg/a_test.py", "top.py"]

    def it_excludes_by_file_name_pattern(tree):
        assert collect(tree, ["*_test.py"]) == ["build/b.py", "pkg/a.py", "top.py"]

    def it_excludes_by_directory_name(tree):
        assert collect(tree, ["build"]) == ["pkg/a.py", "pkg/a_test.py", "top.py"]

    def it_excludes_by_relative_path(tree):
        assert collect(tree, ["pkg/a.py"]) == ["build/b.py", "pkg/a_test.py", "top.py"]

    def it_does_not_match_a_directory_pattern_against_a_partial_path(tree):
        assert collect(tree, ["pkg/a"]) == ["build/b.py", "pkg/a.py", "pkg/a_test.py", "top.py"]

    def it_returns_every_file_when_no_suffixes_are_given(tree):
        found = [p.relative_to(tree).as_posix() for p in collect_files(tree, exclude=["build"])]
        assert found == ["pkg/a.py", "pkg/a_test.py", "pkg/notes.md", "top.py"]

    def it_returns_nothing_for_an_empty_directory(tmp_path):
        assert collect_files(tmp_path, suffixes={".py"}, exclude=[]) == []
