from pathlib import Path

import pytest

from gbnf_experiment.prepare_filesystem.assemble_reference_implementation import (
    assemble_reference_implementation,
)


COLOCATED_TEST = {"typescript": "src/gbnf.test.ts", "python": "gbnf/parse_test.py"}
NESTED_COLOCATED_TEST = {
    "typescript": "src/utils/is-point-in-range.test.ts",
    "python": "gbnf/utils/is_point_in_range_test.py",
}
IMPLEMENTATION = {"typescript": "src/gbnf.ts", "python": "gbnf/parse.py"}
MANIFEST = {"typescript": "package.json", "python": "pyproject.toml"}
COLOCATED_TEST_PATTERN = {"typescript": "*.test.ts", "python": "*_test.py"}
CACHE_ARTEFACTS = (
    "gbnf/__pycache__/parse_test.cpython-314-pytest-9.1.1.pyc",
    ".pytest_cache/CACHEDIR.TAG",
)
FLAGS = [
    {"include_typescript_tests": typescript, "include_python_tests": python}
    for typescript in (False, True)
    for python in (False, True)
]


@pytest.fixture
def prepared_directory(tmp_path):
    directory = tmp_path / "prepared"
    for language in ("typescript", "python"):
        source = directory / "source" / language
        source.mkdir(parents=True)
        (source / MANIFEST[language]).write_text(language)
        for name in (
            IMPLEMENTATION[language],
            COLOCATED_TEST[language],
            NESTED_COLOCATED_TEST[language],
        ):
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(name)
        if language == "python":
            for name in CACHE_ARTEFACTS:
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"\x00compiled")
        tests = directory / "tests" / language
        tests.mkdir(parents=True)
        (tests / f"suite_{language}").write_text(language)
    return directory


@pytest.fixture
def output_directory(tmp_path):
    return tmp_path / "data" / "20260906T142530Z_9f2b1c04" / "reference_implementation"


def surviving_colocated_tests(source: Path, language: str) -> list[str]:
    """Every colocated test of one language left anywhere under the tree."""
    return sorted(
        str(path.relative_to(source))
        for path in source.rglob(COLOCATED_TEST_PATTERN[language])
    )


def describe_assemble_reference_implementation():
    def it_returns_the_output_directory(prepared_directory, output_directory):
        assembled, *_ = assemble_reference_implementation(
            prepared_directory=prepared_directory,
            output_directory=output_directory,
            source_language="typescript",
            include_typescript_tests=False,
            include_python_tests=False,
        )
        assert assembled == output_directory

    def it_copies_the_requested_source_language(prepared_directory, output_directory):
        assemble_reference_implementation(
            prepared_directory=prepared_directory,
            output_directory=output_directory,
            source_language="typescript",
            include_typescript_tests=False,
            include_python_tests=False,
        )
        assert (output_directory / "source" / MANIFEST["typescript"]).read_text() == (
            "typescript"
        )

    def it_copies_the_other_source_language_when_asked(prepared_directory, output_directory):
        assemble_reference_implementation(
            prepared_directory=prepared_directory,
            output_directory=output_directory,
            source_language="python",
            include_typescript_tests=False,
            include_python_tests=False,
        )
        assert (output_directory / "source" / MANIFEST["python"]).read_text() == "python"

    def it_rejects_a_language_with_no_prepared_source(prepared_directory, output_directory):
        with pytest.raises(ValueError, match="No prepared source for language: rust"):
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="rust",
                include_typescript_tests=False,
                include_python_tests=False,
            )

    def describe_tests():
        def it_leaves_the_tests_directory_empty_when_neither_is_asked_for(
            prepared_directory, output_directory
        ):
            """Empty, not absent: the harness mounts tests/ unconditionally."""
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=False,
                include_python_tests=False,
            )
            assert list((output_directory / "tests").iterdir()) == []

        def it_includes_only_the_typescript_suite(prepared_directory, output_directory):
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=True,
                include_python_tests=False,
            )
            assert (output_directory / "tests" / "typescript" / "suite_typescript").is_file()
            assert not (output_directory / "tests" / "python").exists()

        def it_includes_only_the_python_suite(prepared_directory, output_directory):
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_python_tests=True,
                include_typescript_tests=False,
            )
            assert (output_directory / "tests" / "python" / "suite_python").is_file()
            assert not (output_directory / "tests" / "typescript").exists()

        def it_includes_both_suites(prepared_directory, output_directory):
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=True,
                include_python_tests=True,
            )
            assert (output_directory / "tests" / "typescript").is_dir()
            assert (output_directory / "tests" / "python").is_dir()

    def describe_the_colocated_tests():
        def it_strips_them_from_a_typescript_reference_when_no_suite_is_included(
            prepared_directory, output_directory
        ):
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=False,
                include_python_tests=False,
            )
            assert not (
                output_directory / "source" / COLOCATED_TEST["typescript"]
            ).exists()

        def it_strips_them_from_a_python_reference_when_no_suite_is_included(
            prepared_directory, output_directory
        ):
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="python",
                include_typescript_tests=False,
                include_python_tests=False,
            )
            assert not (output_directory / "source" / COLOCATED_TEST["python"]).exists()

        def it_withholds_them_even_when_the_typescript_suite_was_included(
            prepared_directory, output_directory
        ):
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=True,
                include_python_tests=False,
            )
            assert not (
                output_directory / "source" / COLOCATED_TEST["typescript"]
            ).exists()

        def it_withholds_them_even_when_the_python_suite_was_included(
            prepared_directory, output_directory
        ):
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="python",
                include_python_tests=True,
                include_typescript_tests=False,
            )
            assert not (output_directory / "source" / COLOCATED_TEST["python"]).exists()

        def it_strips_a_typescript_reference_the_python_flag_left_alone(
            prepared_directory, output_directory
        ):
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_python_tests=True,
                include_typescript_tests=False,
            )
            assert not (
                output_directory / "source" / COLOCATED_TEST["typescript"]
            ).exists()

        def it_leaves_none_anywhere_when_the_language_was_excluded(
            prepared_directory, output_directory
        ):
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=False,
                include_python_tests=False,
            )
            assert (
                surviving_colocated_tests(output_directory / "source", "typescript")
                == []
            )

        def it_leaves_none_anywhere_even_when_the_language_was_included(
            prepared_directory, output_directory
        ):
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=True,
                include_python_tests=False,
            )
            assert (
                surviving_colocated_tests(output_directory / "source", "typescript")
                == []
            )

        def it_leaves_the_implementation_untouched(
            prepared_directory, output_directory
        ):
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=False,
                include_python_tests=False,
            )
            source = output_directory / "source"
            assert (source / MANIFEST["typescript"]).read_text() == "typescript"
            assert (source / IMPLEMENTATION["typescript"]).read_text() == (
                IMPLEMENTATION["typescript"]
            )

        def it_does_not_touch_the_mounted_suites(prepared_directory, output_directory):
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_python_tests=True,
                include_typescript_tests=False,
            )
            assert (output_directory / "tests" / "python" / "suite_python").is_file()

        def it_strips_the_copy_and_not_the_prepared_corpus(
            prepared_directory, output_directory
        ):
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=False,
                include_python_tests=False,
            )

            assert (
                prepared_directory / "source" / "typescript" / COLOCATED_TEST["typescript"]
            ).is_file()

    def describe_the_cache_artefacts():
        @pytest.mark.parametrize("flags", FLAGS)
        def it_copies_none_of_them_into_a_python_reference(
            prepared_directory, output_directory, flags
        ):
            """Compiled tests are readable: a .pyc decompiles back to its source."""
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="python",
                **flags,
            )
            source = output_directory / "source"
            assert [name for name in CACHE_ARTEFACTS if (source / name).exists()] == []

    def describe_rebuilding():
        def it_removes_stale_contents(prepared_directory, output_directory):
            output_directory.mkdir(parents=True)
            (output_directory / "stale.txt").write_text("old")

            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=False,
                include_python_tests=False,
            )

            assert not (output_directory / "stale.txt").exists()
            assert (output_directory / "source").is_dir()

        def it_drops_a_suite_that_is_no_longer_requested(
            prepared_directory, output_directory
        ):
            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_python_tests=True,
                include_typescript_tests=False,
            )

            assemble_reference_implementation(
                prepared_directory=prepared_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=False,
                include_python_tests=False,
            )

            assert list((output_directory / "tests").iterdir()) == []
