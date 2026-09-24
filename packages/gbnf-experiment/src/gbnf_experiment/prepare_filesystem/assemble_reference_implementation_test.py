from pathlib import Path

import pytest

from gbnf_experiment.prepare_filesystem.assemble_reference_implementation import (
    assemble_reference_implementation,
)

FILES = [Path("package.json"), Path("src/gbnf.ts")]
TEST_FILES = [Path("python/suite_python"), Path("python/grammars/arithmetic.gbnf")]


@pytest.fixture
def prepared_directory(tmp_path):
    directory = tmp_path / "prepared"
    for language in ("typescript", "python"):
        source = directory / "source" / language
        source.mkdir(parents=True)
        (source / "package.json").write_text(language)
        (source / "src").mkdir()
        (source / "src" / "gbnf.ts").write_text(f"{language} source")
        (source / "src" / "gbnf.test.ts").write_text(f"{language} colocated test")
        tests = directory / "tests" / language
        (tests / "grammars").mkdir(parents=True)
        (tests / f"suite_{language}").write_text(language)
        (tests / "grammars" / "arithmetic.gbnf").write_text("root ::= 'x'")
    return directory


@pytest.fixture
def output_directory(tmp_path):
    return tmp_path / "data" / "20260906T142530Z_9f2b1c04" / "reference_implementation"


@pytest.fixture
def assemble(prepared_directory, output_directory):
    def run(**overrides):
        return assemble_reference_implementation(
            **{
                "prepared_directory": prepared_directory,
                "output_directory": output_directory,
                "source_language": "typescript",
                "files": FILES,
                "test_files": [],
                **overrides,
            }
        )

    return run


def tree(directory: Path) -> list[str]:
    return sorted(
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file()
    )


def describe_assemble_reference_implementation():
    def it_returns_the_output_directory(assemble, output_directory):
        assert assemble() == output_directory

    def it_copies_exactly_the_named_files_under_source(assemble, output_directory):
        assemble()
        assert tree(output_directory) == ["source/package.json", "source/src/gbnf.ts"]

    def it_copies_from_the_requested_source_language(assemble, output_directory):
        assemble(source_language="python")
        assert (output_directory / "source" / "package.json").read_text() == "python"

    def it_copies_rather_than_moves(assemble, prepared_directory):
        assemble()
        assert (prepared_directory / "source" / "typescript" / "src" / "gbnf.ts").is_file()

    def describe_tests():
        def it_writes_no_tests_directory_when_no_suite_file_is_named(
            assemble, output_directory
        ):
            """Absent, not empty: the harness mounts tests/ only when it exists."""
            assemble()
            assert not (output_directory / "tests").exists()

        def it_copies_the_named_suite_files_under_tests(assemble, output_directory):
            assemble(test_files=TEST_FILES)
            assert tree(output_directory / "tests") == [
                "python/grammars/arithmetic.gbnf",
                "python/suite_python",
            ]

    def describe_rebuilding():
        def it_removes_stale_contents(assemble, output_directory):
            output_directory.mkdir(parents=True)
            (output_directory / "stale.txt").write_text("old")
            assemble()
            assert not (output_directory / "stale.txt").exists()

        def it_drops_a_suite_that_is_no_longer_named(assemble, output_directory):
            assemble(test_files=TEST_FILES)
            assemble()
            assert not (output_directory / "tests").exists()
