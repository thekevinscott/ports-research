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
COLOCATED_TEST_PATTERN = {"typescript": "*.test.ts", "python": "*_test.py"}


@pytest.fixture
def derivation_directory(tmp_path):
    directory = tmp_path / "derivation"
    for language in ("typescript", "python"):
        source = directory / "source" / language
        source.mkdir(parents=True)
        (source / f"index.{language}").write_text(language)
        for name in (
            IMPLEMENTATION[language],
            COLOCATED_TEST[language],
            NESTED_COLOCATED_TEST[language],
        ):
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(name)
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
    def it_returns_the_output_directory(derivation_directory, output_directory):
        assembled = assemble_reference_implementation(
            derivation_directory=derivation_directory,
            output_directory=output_directory,
            source_language="typescript",
            include_typescript_tests=False,
            include_python_tests=False,
        )
        assert assembled == output_directory

    def it_copies_the_requested_source_language(derivation_directory, output_directory):
        assemble_reference_implementation(
            derivation_directory=derivation_directory,
            output_directory=output_directory,
            source_language="typescript",
            include_typescript_tests=False,
            include_python_tests=False,
        )
        assert (output_directory / "source" / "index.typescript").read_text() == "typescript"

    def it_copies_the_other_source_language_when_asked(derivation_directory, output_directory):
        assemble_reference_implementation(
            derivation_directory=derivation_directory,
            output_directory=output_directory,
            source_language="python",
            include_typescript_tests=False,
            include_python_tests=False,
        )
        assert (output_directory / "source" / "index.python").read_text() == "python"

    def it_rejects_a_language_with_no_derived_source(derivation_directory, output_directory):
        with pytest.raises(ValueError, match="No derived source for language: rust"):
            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="rust",
                include_typescript_tests=False,
                include_python_tests=False,
            )

    def describe_tests():
        def it_leaves_the_tests_directory_empty_when_neither_is_asked_for(
            derivation_directory, output_directory
        ):
            """Empty, not absent: the harness mounts tests/ unconditionally."""
            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=False,
                include_python_tests=False,
            )
            assert list((output_directory / "tests").iterdir()) == []

        def it_includes_only_the_typescript_suite(derivation_directory, output_directory):
            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=True,
                include_python_tests=False,
            )
            assert (output_directory / "tests" / "typescript" / "suite_typescript").is_file()
            assert not (output_directory / "tests" / "python").exists()

        def it_includes_only_the_python_suite(derivation_directory, output_directory):
            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_python_tests=True,
                include_typescript_tests=False,
            )
            assert (output_directory / "tests" / "python" / "suite_python").is_file()
            assert not (output_directory / "tests" / "typescript").exists()

        def it_includes_both_suites(derivation_directory, output_directory):
            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=True,
                include_python_tests=True,
            )
            assert (output_directory / "tests" / "typescript").is_dir()
            assert (output_directory / "tests" / "python").is_dir()

    def describe_the_colocated_tests():
        def it_strips_them_from_a_typescript_reference_when_no_suite_is_included(
            derivation_directory, output_directory
        ):
            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=False,
                include_python_tests=False,
            )
            assert not (
                output_directory / "source" / COLOCATED_TEST["typescript"]
            ).exists()

        def it_strips_them_from_a_python_reference_when_no_suite_is_included(
            derivation_directory, output_directory
        ):
            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="python",
                include_typescript_tests=False,
                include_python_tests=False,
            )
            assert not (output_directory / "source" / COLOCATED_TEST["python"]).exists()

        def it_keeps_them_when_the_typescript_suite_was_included(
            derivation_directory, output_directory
        ):
            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=True,
                include_python_tests=False,
            )
            assert (output_directory / "source" / COLOCATED_TEST["typescript"]).is_file()

        def it_keeps_them_when_the_python_suite_was_included(
            derivation_directory, output_directory
        ):
            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="python",
                include_python_tests=True,
                include_typescript_tests=False,
            )
            assert (output_directory / "source" / COLOCATED_TEST["python"]).is_file()

        def it_strips_a_typescript_reference_the_python_flag_left_alone(
            derivation_directory, output_directory
        ):
            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_python_tests=True,
                include_typescript_tests=False,
            )
            assert not (
                output_directory / "source" / COLOCATED_TEST["typescript"]
            ).exists()

        def it_leaves_none_anywhere_when_the_language_was_excluded(
            derivation_directory, output_directory
        ):
            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=False,
                include_python_tests=False,
            )
            assert (
                surviving_colocated_tests(output_directory / "source", "typescript")
                == []
            )

        def it_leaves_them_all_when_the_language_was_included(
            derivation_directory, output_directory
        ):
            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=True,
                include_python_tests=False,
            )
            assert surviving_colocated_tests(
                output_directory / "source", "typescript"
            ) == sorted(
                [COLOCATED_TEST["typescript"], NESTED_COLOCATED_TEST["typescript"]]
            )

        def it_leaves_the_implementation_untouched(
            derivation_directory, output_directory
        ):
            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=False,
                include_python_tests=False,
            )
            source = output_directory / "source"
            assert (source / "index.typescript").read_text() == "typescript"
            assert (source / IMPLEMENTATION["typescript"]).read_text() == (
                IMPLEMENTATION["typescript"]
            )

        def it_does_not_touch_the_mounted_suites(derivation_directory, output_directory):
            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_python_tests=True,
                include_typescript_tests=False,
            )
            assert (output_directory / "tests" / "python" / "suite_python").is_file()

        def it_strips_the_copy_and_not_the_derivation(
            derivation_directory, output_directory
        ):
            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=False,
                include_python_tests=False,
            )

            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=True,
                include_python_tests=False,
            )

            assert (output_directory / "source" / COLOCATED_TEST["typescript"]).is_file()

    def describe_rebuilding():
        def it_removes_stale_contents(derivation_directory, output_directory):
            output_directory.mkdir(parents=True)
            (output_directory / "stale.txt").write_text("old")

            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=False,
                include_python_tests=False,
            )

            assert not (output_directory / "stale.txt").exists()
            assert (output_directory / "source").is_dir()

        def it_drops_a_suite_that_is_no_longer_requested(
            derivation_directory, output_directory
        ):
            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_python_tests=True,
                include_typescript_tests=False,
            )

            assemble_reference_implementation(
                derivation_directory=derivation_directory,
                output_directory=output_directory,
                source_language="typescript",
                include_typescript_tests=False,
                include_python_tests=False,
            )

            assert list((output_directory / "tests").iterdir()) == []
