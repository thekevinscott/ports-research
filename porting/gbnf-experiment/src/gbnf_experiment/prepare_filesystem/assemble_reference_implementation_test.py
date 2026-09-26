from pathlib import Path

import pytest

from gbnf_experiment.prepare_filesystem.assemble_reference_implementation import (
    assemble_reference_implementation,
)

FILES = [Path("source/typescript/package.json"), Path("source/typescript/src/gbnf.ts")]
SUITE = [Path("tests/python/suite_python"), Path("tests/python/grammars/arithmetic.gbnf")]


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
    def run(files=FILES):
        return assemble_reference_implementation(
            source=prepared_directory, output=output_directory, files=files
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

    def it_copies_exactly_the_named_files_at_their_own_paths(assemble, output_directory):
        assemble()
        assert tree(output_directory) == [path.as_posix() for path in FILES]

    def it_copies_content_not_just_names(assemble, output_directory):
        assemble()
        assert (output_directory / "source/typescript/package.json").read_text() == "typescript"

    def it_copies_rather_than_moves(assemble, prepared_directory):
        assemble()
        assert (prepared_directory / "source/typescript/src/gbnf.ts").is_file()

    def it_writes_no_directory_nothing_was_named_under(assemble, output_directory):
        """Absent, not empty: the harness mounts tests/ only when it exists."""
        assemble()
        assert not (output_directory / "tests").exists()

    def it_writes_nothing_for_an_empty_list(assemble, output_directory):
        assemble(files=[])
        assert tree(output_directory) == []

    def describe_rebuilding():
        def it_removes_stale_contents(assemble, output_directory):
            output_directory.mkdir(parents=True)
            (output_directory / "stale.txt").write_text("old")
            assemble()
            assert not (output_directory / "stale.txt").exists()

        def it_drops_a_file_that_is_no_longer_named(assemble, output_directory):
            assemble(files=[*FILES, *SUITE])
            assemble()
            assert not (output_directory / "tests").exists()
