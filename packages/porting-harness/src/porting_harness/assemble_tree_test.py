from pathlib import Path

import pytest

from porting_harness.assemble_tree import assemble_tree

TREE = {
    "pyproject.toml": "[project]",
    "README.md": "# gbnf",
    "Makefile": "test:",
    "pkg/__init__.py": "",
    "pkg/parse.py": "def parse(): ...",
    "pkg/parse_test.py": "def test_parse(): ...",
    "pkg/utils/is_point_in_range.py": "def is_point_in_range(): ...",
    "pkg/__pycache__/mod_test.cpython-314-pytest-9.1.1.pyc": "\x00compiled",
    "pkg/__pycache__/parse.cpython-314.pyc": "\x00compiled",
    ".pytest_cache/CACHEDIR.TAG": "Signature: 8a477f597d28d172",
    "dev/browser/index.html": "<html>",
}


def relative_files(directory: Path) -> list[str]:
    return sorted(
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file()
    )


@pytest.fixture
def source(tmp_path):
    directory = tmp_path / "source"
    for name, contents in TREE.items():
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
    return directory


@pytest.fixture
def destination(tmp_path):
    return tmp_path / "destination"


@pytest.fixture
def assemble(source, destination):
    def call(*patterns):
        return assemble_tree(
            source=source, destination=destination, patterns=list(patterns)
        )

    return call


def describe_assemble_tree():
    def it_copies_a_file_a_pattern_names(assemble, destination):
        assemble("pyproject.toml")
        assert (destination / "pyproject.toml").read_text() == "[project]"

    def it_copies_nothing_a_pattern_does_not_name(assemble, destination):
        assemble("pyproject.toml")
        assert relative_files(destination) == ["pyproject.toml"]

    def it_copies_nothing_at_all_without_patterns(assemble, destination):
        assemble()
        assert not destination.exists()

    def it_takes_several_named_files(assemble, destination):
        assemble("pyproject.toml", "README.md")
        assert relative_files(destination) == ["README.md", "pyproject.toml"]

    def describe_globs():
        def it_takes_a_directory_whole(assemble, destination):
            assemble("pkg/**")
            assert relative_files(destination) == [
                "pkg/__init__.py",
                "pkg/__pycache__/mod_test.cpython-314-pytest-9.1.1.pyc",
                "pkg/__pycache__/parse.cpython-314.pyc",
                "pkg/parse.py",
                "pkg/parse_test.py",
                "pkg/utils/is_point_in_range.py",
            ]

        def it_takes_one_suffix_at_any_depth(assemble, destination):
            assemble("pkg/**/*.py")
            assert relative_files(destination) == [
                "pkg/__init__.py",
                "pkg/parse.py",
                "pkg/parse_test.py",
                "pkg/utils/is_point_in_range.py",
            ]

        def it_keeps_a_nested_path_nested(assemble, destination):
            assemble("pkg/**/*.py")
            assert (destination / "pkg" / "utils" / "is_point_in_range.py").is_file()

        def it_leaves_a_directory_of_unnamed_files_alone(assemble, destination):
            assemble("pkg/**/*.py")
            assert not (destination / "dev").exists()

    def describe_negation():
        def it_drops_a_file_a_later_pattern_excludes(assemble, destination):
            assemble("pkg/**/*.py", "!**/*_test.py")
            assert relative_files(destination) == [
                "pkg/__init__.py",
                "pkg/parse.py",
                "pkg/utils/is_point_in_range.py",
            ]

        def it_excludes_nothing_that_was_never_included(assemble, destination):
            assemble("README.md", "!**/*_test.py")
            assert relative_files(destination) == ["README.md"]

    def describe_the_artefacts_a_blacklist_let_through():
        def it_copies_neither_pycache_nor_pytest_cache(assemble, destination):
            assemble("pkg/**/*.py")
            assert relative_files(destination) == [
                "pkg/__init__.py",
                "pkg/parse.py",
                "pkg/parse_test.py",
                "pkg/utils/is_point_in_range.py",
            ]
            assert not (destination / "pkg" / "__pycache__").exists()
            assert not (destination / ".pytest_cache").exists()

    def describe_directories():
        def it_creates_no_empty_directory(assemble, destination):
            assemble("pkg/*.py")
            assert [
                path.relative_to(destination).as_posix()
                for path in destination.rglob("*")
                if path.is_dir()
            ] == ["pkg"]

        def it_creates_the_destination_parents_it_needs(assemble, destination):
            assemble("pkg/utils/*.py")
            assert (destination / "pkg" / "utils" / "is_point_in_range.py").is_file()

    def describe_symlinks():
        def it_does_not_copy_a_symlinked_file(assemble, source, destination):
            (source / "pkg" / "alias.py").symlink_to(source / "pkg" / "parse_test.py")
            assemble("pkg/**/*.py")
            assert not (destination / "pkg" / "alias.py").exists()

        def it_does_not_descend_into_a_symlinked_directory(
            assemble, source, destination
        ):
            (source / "pkg" / "mirror").symlink_to(source / "pkg" / "utils")
            assemble("pkg/**/*.py")
            assert not (destination / "pkg" / "mirror").exists()

        def it_reports_a_symlink_as_excluded(assemble, source):
            (source / "pkg" / "alias.py").symlink_to(source / "pkg" / "parse_test.py")
            assert "pkg/alias.py" in assemble("pkg/**/*.py").excluded

    def describe_the_report():
        def it_lists_the_patterns_it_was_given(assemble):
            assert assemble("pkg/**/*.py", "!**/*_test.py").patterns == (
                "pkg/**/*.py",
                "!**/*_test.py",
            )

        def it_lists_every_copied_path_sorted(assemble):
            assert assemble("pkg/*.py").included == (
                "pkg/__init__.py",
                "pkg/parse.py",
                "pkg/parse_test.py",
            )

        def it_lists_every_withheld_path_sorted(assemble):
            report = assemble("pkg/*.py")
            assert report.excluded == tuple(
                sorted(set(TREE) - set(report.included))
            )

        def it_accounts_for_every_file_in_the_source(assemble):
            report = assemble("pkg/**/*.py", "!**/*_test.py")
            assert sorted([*report.included, *report.excluded]) == sorted(TREE)
