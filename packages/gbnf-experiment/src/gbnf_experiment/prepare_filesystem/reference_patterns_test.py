from pathlib import Path

import pytest

from gbnf_experiment.prepare_filesystem.reference_patterns import PATTERNS, TEST_PATTERNS
from porting_harness.select_files import select_files

COLOCATED_TESTS = {
    "typescript": ("src/gbnf.test.ts", "src/utils/is-point-in-range.test.ts"),
    "python": ("gbnf/parse_test.py", "gbnf/utils/is_point_in_range_test.py"),
}
IMPLEMENTATION = {"typescript": "src/gbnf.ts", "python": "gbnf/parse.py"}
MANIFEST = {"typescript": "package.json", "python": "pyproject.toml"}
CACHE_ARTEFACTS = (
    "gbnf/__pycache__/parse_test.cpython-314-pytest-9.1.1.pyc",
    ".pytest_cache/CACHEDIR.TAG",
)
DEV_HARNESS = ("dev/browser/debug/index.html", "dev/node/src/commands/parse.ts")


def write(directory: Path, names: tuple[str, ...]) -> None:
    for name in names:
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(name)


@pytest.fixture
def source(tmp_path):
    for language in ("typescript", "python"):
        write(
            tmp_path / language,
            (MANIFEST[language], IMPLEMENTATION[language], *COLOCATED_TESTS[language]),
        )
    write(tmp_path / "python", CACHE_ARTEFACTS)
    write(tmp_path / "typescript", DEV_HARNESS)
    return tmp_path


@pytest.fixture
def tests(tmp_path):
    for language in ("typescript", "python"):
        write(tmp_path / language, ("iteration/grammars_test", "validation/validate_test"))
    write(tmp_path / "python", ("iteration/grammars/arithmetic.gbnf",))
    return tmp_path


def selected(source: Path, language: str) -> list[str]:
    return [
        path.as_posix()
        for path in select_files(source=source / language, patterns=PATTERNS[language])
    ]


def describe_patterns():
    @pytest.mark.parametrize("language", ["typescript", "python"])
    def it_keeps_the_implementation_and_its_manifest(source, language):
        assert selected(source, language) == sorted(
            [MANIFEST[language], IMPLEMENTATION[language]]
        )

    @pytest.mark.parametrize("language", ["typescript", "python"])
    def it_withholds_the_colocated_tests_at_every_depth(source, language):
        assert not set(COLOCATED_TESTS[language]) & set(selected(source, language))

    def it_leaves_the_compiled_tests_behind(source):
        """A .pyc decompiles back to its source."""
        assert not set(CACHE_ARTEFACTS) & set(selected(source, "python"))

    def it_hides_the_typescript_dev_harness(source):
        """dev/ is browser and node demo apps, not the library under port."""
        assert not set(DEV_HARNESS) & set(selected(source, "typescript"))


def describe_test_patterns():
    def it_names_one_suite_with_its_fixtures(tests):
        assert [
            path.as_posix()
            for path in select_files(source=tests, patterns=[TEST_PATTERNS["python"]])
        ] == [
            "python/iteration/grammars/arithmetic.gbnf",
            "python/iteration/grammars_test",
            "python/validation/validate_test",
        ]

    def it_names_nothing_when_given_no_pattern(tests):
        assert select_files(source=tests, patterns=[]) == []
