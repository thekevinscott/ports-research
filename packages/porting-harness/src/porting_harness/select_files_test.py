import pytest

from porting_harness.select_files import select_files

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
    "dev/browser/README.md": "# demo app",
}


@pytest.fixture
def listing():
    return list(TREE)


@pytest.fixture
def select(listing):
    def call(*patterns):
        return select_files(paths=listing, patterns=list(patterns))

    return call


def describe_select_files():
    def it_returns_a_file_a_pattern_names(select):
        assert select("pyproject.toml") == ["pyproject.toml"]

    def it_returns_nothing_at_all_without_patterns(select):
        assert select() == []

    def it_takes_several_named_files(select):
        assert select("/pyproject.toml", "/README.md") == [
            "README.md",
            "pyproject.toml",
        ]

    def describe_globs():
        def it_takes_a_directory_whole(select):
            assert select("pkg/**") == [
                "pkg/__init__.py",
                "pkg/__pycache__/mod_test.cpython-314-pytest-9.1.1.pyc",
                "pkg/__pycache__/parse.cpython-314.pyc",
                "pkg/parse.py",
                "pkg/parse_test.py",
                "pkg/utils/is_point_in_range.py",
            ]

        def it_takes_one_suffix_at_any_depth(select):
            assert select("pkg/**/*.py") == [
                "pkg/__init__.py",
                "pkg/parse.py",
                "pkg/parse_test.py",
                "pkg/utils/is_point_in_range.py",
            ]

        def it_leaves_a_directory_of_unnamed_files_alone(select):
            assert [name for name in select("pkg/**/*.py") if "dev/" in name] == []

    def describe_anchoring():
        def it_matches_a_bare_name_at_any_depth(select):
            assert select("README.md") == ["README.md", "dev/browser/README.md"]

        def it_matches_a_leading_slash_at_the_root_only(select):
            assert select("/README.md") == ["README.md"]

    def describe_negation():
        def it_drops_a_file_a_later_pattern_excludes(select):
            assert select("pkg/**/*.py", "!**/*_test.py") == [
                "pkg/__init__.py",
                "pkg/parse.py",
                "pkg/utils/is_point_in_range.py",
            ]

        def it_excludes_nothing_that_was_never_included(select):
            assert select("/README.md", "!**/*_test.py") == ["README.md"]

    def describe_the_artefacts_a_blacklist_let_through():
        def it_returns_neither_pycache_nor_pytest_cache(select):
            selected = select("pkg/**/*.py")
            assert [
                name
                for name in selected
                if "__pycache__" in name or name.startswith(".pytest_cache")
            ] == []
