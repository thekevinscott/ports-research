from pathlib import Path

import pytest

from gbnf_experiment.prepare_filesystem.included_files import included_files


@pytest.fixture
def reference(tmp_path) -> Path:
    directory = tmp_path / "reference"
    (directory / "source" / "src").mkdir(parents=True)
    (directory / "source" / "package.json").write_text("{}")
    (directory / "source" / "src" / "index.ts").write_text("export {};")
    (directory / "tests" / "python").mkdir(parents=True)
    (directory / "tests" / "python" / "gbnf_test.py").write_text("def test(): ...")
    return directory


def describe_included_files():
    def it_lists_every_file_relative_to_the_reference_root(reference):
        assert included_files(reference) == [
            Path("source/package.json"),
            Path("source/src/index.ts"),
            Path("tests/python/gbnf_test.py"),
        ]

    def it_omits_directories(reference):
        assert all(path != Path("source/src") for path in included_files(reference))

    def it_omits_symlinks(reference):
        """A symlink names a path the image did not put in the corpus."""
        (reference / "source" / "link.ts").symlink_to(reference / "source" / "src" / "index.ts")
        assert Path("source/link.ts") not in included_files(reference)

    def it_returns_nothing_for_an_empty_reference(tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        assert included_files(empty) == []
