from pathlib import Path
from unittest.mock import patch

import pytest

from round_trip_experiment.format_tree import format_tree


@pytest.fixture
def root(tmp_path):
    return tmp_path


def write(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def describe_format_tree():
    def it_formats_python_in_place(root):
        path = write(root, "pkg/m.py", "def f( a ):\n    return a+1\n")
        format_tree("python", root, [path])
        assert path.read_text() == "def f(a):\n    return a + 1\n"

    def it_sorts_python_imports(root):
        path = write(root, "pkg/m.py", "import sys\nimport os\n\nprint(os, sys)\n")
        format_tree("python", root, [path])
        assert path.read_text().splitlines()[:2] == ["import os", "import sys"]

    def it_reports_nothing_when_every_file_formats(root):
        path = write(root, "pkg/m.py", "x = 1\n")
        assert format_tree("python", root, [path]) == []

    def it_reports_the_relative_path_of_a_file_the_formatter_refuses(root):
        good, bad = write(root, "pkg/m.py", "x = 1\n"), write(root, "pkg/bad.py", "def (:\n")
        assert format_tree("python", root, [good, bad]) == ["pkg/bad.py"]

    def it_still_formats_the_files_around_a_refusal(root):
        good, bad = write(root, "pkg/m.py", "x=1\n"), write(root, "pkg/bad.py", "def (:\n")
        format_tree("python", root, [good, bad])
        assert good.read_text() == "x = 1\n"

    def it_reports_a_refusal_once_however_many_commands_reject_it(root):
        bad = write(root, "pkg/bad.py", "def (:\n")
        assert format_tree("python", root, [bad]) == ["pkg/bad.py"]

    def it_runs_nothing_for_an_empty_file_list(root):
        with patch("round_trip_experiment.format_tree.subprocess", autospec=True) as m:
            assert format_tree("python", root, []) == []
            m.run.assert_not_called()

    def it_runs_prettier_through_pnpm_dlx_not_npx(root):
        path = write(root, "s.ts", "const a = 1;\n")
        with patch("round_trip_experiment.format_tree.subprocess", autospec=True) as m:
            m.run.return_value.returncode = 0
            format_tree("typescript", root, [path])
        argv = m.run.call_args.args[0]
        assert argv[:2] == ["pnpm", "dlx"]
        assert argv[2].startswith("prettier@")
        assert "npx" not in argv
