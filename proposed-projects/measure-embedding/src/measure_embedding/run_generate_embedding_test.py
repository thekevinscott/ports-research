from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from measure_embedding.run_generate_embedding import GENERATE_EMBEDDING_DIR, run_generate_embedding


@pytest.fixture
def run():
    with patch("subprocess.run", autospec=True) as m:
        m.return_value = Mock(returncode=0, stdout="/out/a.py.npy\n", stderr="")
        yield m


def describe_run_generate_embedding():
    def it_points_at_the_generate_embedding_package():
        assert GENERATE_EMBEDDING_DIR.parent.name == "packages"
        assert GENERATE_EMBEDDING_DIR.name == "generate-embedding"

    def it_drives_the_generate_embedding_cli_with_output(run):
        run_generate_embedding(Path("/src/a.py"), Path("/out/a.py.npy"), model="m")
        assert run.call_args.args[0] == [
            "uv", "run", "--directory", str(GENERATE_EMBEDDING_DIR),
            "generate-embedding", "/src/a.py", "--model", "m", "--output", "/out/a.py.npy",
        ]

    def it_captures_output_as_text(run):
        run_generate_embedding(Path("/src/a.py"), Path("/out/a.py.npy"), model="m")
        assert run.call_args.kwargs["capture_output"] is True
        assert run.call_args.kwargs["text"] is True

    def it_raises_with_stderr_when_the_cli_fails(run):
        run.return_value = Mock(returncode=1, stdout="", stderr="Error: boom")
        with pytest.raises(RuntimeError, match="boom"):
            run_generate_embedding(Path("/src/a.py"), Path("/out/a.py.npy"), model="m")
