import pytest

from gbnf_experiment.prepare_filesystem.reference_patterns import reference_patterns
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
SUITES = {
    "typescript": ("iteration/grammars.test.ts", "validation/validate.test.ts"),
    "python": (
        "iteration/grammars_test.py",
        "iteration/grammars/arithmetic.gbnf",
        "validation/validate_test.py",
    ),
}


def under(root: str, names) -> set[str]:
    return {f"{root}/{name}" for name in names}


@pytest.fixture
def prepared() -> list[str]:
    """The prepare stage's listing: every file under /prepared, relative."""
    listing: set[str] = set()
    for language in ("typescript", "python"):
        listing |= under(
            f"reference_implementation/{language}",
            (MANIFEST[language], IMPLEMENTATION[language], *COLOCATED_TESTS[language]),
        )
        listing |= under(f"tests/{language}", SUITES[language])
    listing |= under("reference_implementation/python", CACHE_ARTEFACTS)
    listing |= under("reference_implementation/typescript", DEV_HARNESS)
    return sorted(listing)


def selected(prepared: list[str], language: str, **flags) -> list[str]:
    patterns = reference_patterns(
        language,
        **{"include_typescript_tests": False, "include_python_tests": False, **flags},
    )
    return [path.as_posix() for path in select_files(paths=prepared, patterns=patterns)]


def describe_reference_patterns():
    @pytest.mark.parametrize("language", ["typescript", "python"])
    def it_keeps_the_implementation_and_its_manifest(prepared, language):
        assert selected(prepared, language) == sorted(
            under(f"reference_implementation/{language}", [MANIFEST[language], IMPLEMENTATION[language]])
        )

    @pytest.mark.parametrize("language", ["typescript", "python"])
    def it_withholds_the_colocated_tests_at_every_depth(prepared, language):
        assert not under(f"reference_implementation/{language}", COLOCATED_TESTS[language]) & set(
            selected(prepared, language)
        )

    @pytest.mark.parametrize("language", ["typescript", "python"])
    def it_never_reaches_the_other_language(prepared, language):
        other = "python" if language == "typescript" else "typescript"
        assert not any(path.startswith(f"reference_implementation/{other}/") for path in selected(prepared, language))

    def it_leaves_the_compiled_tests_behind(prepared):
        """A .pyc decompiles back to its source."""
        assert not under("reference_implementation/python", CACHE_ARTEFACTS) & set(selected(prepared, "python"))

    def it_hides_the_typescript_dev_harness(prepared):
        """dev/ is browser and node demo apps, not the library under port."""
        assert not under("reference_implementation/typescript", DEV_HARNESS) & set(
            selected(prepared, "typescript")
        )

    def describe_the_generated_suites():
        def it_names_none_by_default(prepared):
            assert not any(path.startswith("tests/") for path in selected(prepared, "typescript"))

        def it_names_one_suite_with_its_fixtures(prepared):
            assert [
                path
                for path in selected(prepared, "typescript", include_python_tests=True)
                if path.startswith("tests/")
            ] == sorted(under("tests/python", SUITES["python"]))

        def it_names_both_when_both_are_asked_for(prepared):
            assert under("tests/typescript", SUITES["typescript"]) <= set(
                selected(
                    prepared,
                    "python",
                    include_typescript_tests=True,
                    include_python_tests=True,
                )
            )

        def it_keeps_a_suite_file_the_colocated_rule_would_drop(prepared):
            """The `_test.py` exclusion is scoped to reference_implementation/, not the suite."""
            assert "tests/python/iteration/grammars_test.py" in selected(
                prepared, "typescript", include_python_tests=True
            )

        def it_leaves_the_source_selection_unchanged(prepared):
            with_suite = selected(prepared, "typescript", include_typescript_tests=True)
            assert [p for p in with_suite if p.startswith("reference_implementation/")] == selected(
                prepared, "typescript"
            )
