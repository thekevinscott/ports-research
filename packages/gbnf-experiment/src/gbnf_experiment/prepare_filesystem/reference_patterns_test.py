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


@pytest.fixture
def listing() -> list[str]:
    """Every path the prepare container leaves under /prepared, as one listing."""
    paths = []
    for language in ("typescript", "python"):
        paths += [
            f"source/{language}/{name}"
            for name in (MANIFEST[language], IMPLEMENTATION[language], *COLOCATED_TESTS[language])
        ]
        paths += [f"tests/{language}/{name}" for name in SUITES[language]]
    paths += [f"source/python/{name}" for name in CACHE_ARTEFACTS]
    paths += [f"source/typescript/{name}" for name in DEV_HARNESS]
    return paths


def selected(listing: list[str], language: str, **flags) -> list[str]:
    patterns = reference_patterns(
        language,
        **{"include_typescript_tests": False, "include_python_tests": False, **flags},
    )
    return [path.as_posix() for path in select_files(paths=listing, patterns=patterns)]


def under(root: str, names) -> set[str]:
    return {f"{root}/{name}" for name in names}


def describe_reference_patterns():
    @pytest.mark.parametrize("language", ["typescript", "python"])
    def it_keeps_the_implementation_and_its_manifest(listing, language):
        assert selected(listing, language) == sorted(
            under(f"source/{language}", [MANIFEST[language], IMPLEMENTATION[language]])
        )

    @pytest.mark.parametrize("language", ["typescript", "python"])
    def it_withholds_the_colocated_tests_at_every_depth(listing, language):
        assert not under(f"source/{language}", COLOCATED_TESTS[language]) & set(
            selected(listing, language)
        )

    @pytest.mark.parametrize("language", ["typescript", "python"])
    def it_never_reaches_the_other_language(listing, language):
        other = "python" if language == "typescript" else "typescript"
        assert not any(path.startswith(f"source/{other}/") for path in selected(listing, language))

    def it_leaves_the_compiled_tests_behind(listing):
        """A .pyc decompiles back to its source."""
        assert not under("source/python", CACHE_ARTEFACTS) & set(selected(listing, "python"))

    def it_hides_the_typescript_dev_harness(listing):
        """dev/ is browser and node demo apps, not the library under port."""
        assert not under("source/typescript", DEV_HARNESS) & set(
            selected(listing, "typescript")
        )

    def describe_the_generated_suites():
        def it_names_none_by_default(listing):
            assert not any(path.startswith("tests/") for path in selected(listing, "typescript"))

        def it_names_one_suite_with_its_fixtures(listing):
            assert [
                path
                for path in selected(listing, "typescript", include_python_tests=True)
                if path.startswith("tests/")
            ] == sorted(under("tests/python", SUITES["python"]))

        def it_names_both_when_both_are_asked_for(listing):
            assert under("tests/typescript", SUITES["typescript"]) <= set(
                selected(
                    listing,
                    "python",
                    include_typescript_tests=True,
                    include_python_tests=True,
                )
            )

        def it_keeps_a_suite_file_the_colocated_rule_would_drop(listing):
            """The `_test.py` exclusion is scoped to source/, not the suite."""
            assert "tests/python/iteration/grammars_test.py" in selected(
                listing, "typescript", include_python_tests=True
            )

        def it_leaves_the_source_selection_unchanged(listing):
            with_suite = selected(listing, "typescript", include_typescript_tests=True)
            assert [p for p in with_suite if p.startswith("source/")] == selected(
                listing, "typescript"
            )
