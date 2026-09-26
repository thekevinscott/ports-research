from pathlib import Path

import pytest

from round_trip_experiment.normalize_tree import normalize_tree

COMMENTED = "import sys\nimport os\n\n\n# note\n# more note\ndef f( a ):\n    return a+1\n"
NORMALIZED = "import os\nimport sys\n\n\ndef f(a):\n    return a + 1\n"


def write_tree(root: Path, files: dict[str, str]) -> Path:
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


@pytest.fixture
def source(tmp_path):
    return write_tree(
        tmp_path / "source",
        {"pkg/m.py": COMMENTED, "pkg/m_test.py": "z = 3\n", "notes.md": "not code"},
    )


@pytest.fixture
def destination(tmp_path):
    return tmp_path / "normalized"


def normalize(source, destination, language="python", exclude=["*_test.py"]):
    return normalize_tree(language=language, source=source, destination=destination, exclude=exclude)


def describe_normalize_tree():
    def it_copies_only_the_source_files_the_excludes_keep(source, destination):
        assert normalize(source, destination)["paths"] == ["pkg/m.py"]

    def it_leaves_the_source_tree_untouched(source, destination):
        normalize(source, destination)
        assert (source / "pkg/m.py").read_text() == COMMENTED

    def it_strips_comments_drops_blank_lines_and_formats(source, destination):
        normalize(source, destination)
        assert (destination / "pkg/m.py").read_text() == NORMALIZED

    def it_keeps_the_relative_layout(source, destination):
        normalize(source, destination)
        assert (destination / "pkg" / "m.py").is_file()

    def it_counts_the_lines_of_the_normalized_copies(source, destination):
        assert normalize(source, destination)["lines"] == 6

    def it_reports_no_formatter_failures_for_a_tree_that_formats(source, destination):
        assert normalize(source, destination)["formatter_failures"] == []

    def it_records_a_file_the_formatter_refuses_without_raising(tmp_path, destination):
        source = write_tree(tmp_path / "source", {"m.py": "x = 1\n", "bad.py": "def (:\n"})
        assert normalize(source, destination)["formatter_failures"] == ["bad.py"]

    def it_still_normalizes_the_files_around_a_refusal(tmp_path, destination):
        source = write_tree(tmp_path / "source", {"m.py": "x=1\n", "bad.py": "def (:\n"})
        normalize(source, destination)
        assert (destination / "m.py").read_text() == "x = 1\n"

    def it_raises_when_the_tree_has_no_source_files(tmp_path, destination):
        source = write_tree(tmp_path / "source", {"notes.md": "not code"})
        with pytest.raises(FileNotFoundError, match="no python source"):
            normalize(source, destination)

    def it_normalizes_typescript_with_prettier(tmp_path, destination):
        source = write_tree(tmp_path / "source", {"s.ts": "// note\nexport const f = (a:number)=>a+1\n"})
        report = normalize(source, destination, language="typescript", exclude=[])
        assert (destination / "s.ts").read_text() == "export const f = (a: number) => a + 1;\n"
        assert (report["paths"], report["lines"]) == (["s.ts"], 1)
