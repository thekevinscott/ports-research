import json
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from click.testing import CliRunner

from generate_embedding.cli import cli

ENV = {"GENERATE_EMBEDDING_BASE_URL": "http://localhost:8080/v1"}


@pytest.fixture
def embeddings_endpoint():
    """The only thing held back is the network: httpx is replaced, everything
    from the CLI down through embed_file and write_vector runs for real."""
    client = MagicMock()
    client.post.return_value.json.return_value = {
        "data": [{"embedding": [0.1, 0.2, 0.3]}],
        "model": "nomic-embed-text",
    }
    with patch("httpx.Client", return_value=client):
        yield client


@pytest.fixture
def code_file(tmp_path):
    path = tmp_path / "add.py"
    path.write_text("def add(a, b):\n    return a + b\n")
    return path


def describe_generate_embedding():
    def it_prints_the_embedding_as_json(embeddings_endpoint, code_file):
        result = CliRunner().invoke(cli, [str(code_file), "--model", "m"], env=ENV)
        assert result.exit_code == 0
        assert json.loads(result.output) == {
            "model": "nomic-embed-text",
            "dimension": 3,
            "embedding": [0.1, 0.2, 0.3],
        }

    def it_sends_the_files_text_to_the_endpoint(embeddings_endpoint, code_file):
        CliRunner().invoke(cli, [str(code_file), "--model", "m"], env=ENV)
        assert embeddings_endpoint.post.call_args.kwargs["json"]["input"] == code_file.read_text()

    def it_writes_a_float32_npy_array_readable_by_numpy(embeddings_endpoint, code_file, tmp_path):
        output = tmp_path / "vec.npy"
        result = CliRunner().invoke(
            cli, [str(code_file), "--model", "m", "--output", str(output)], env=ENV
        )
        assert result.exit_code == 0
        loaded = np.load(output)
        assert loaded.dtype == np.float32
        np.testing.assert_allclose(loaded, [0.1, 0.2, 0.3], rtol=1e-6)

    def it_reports_a_missing_path_as_a_usage_error(embeddings_endpoint, tmp_path):
        result = CliRunner().invoke(cli, [str(tmp_path / "missing.py"), "--model", "m"], env=ENV)
        assert result.exit_code != 0

    def it_requires_a_model(embeddings_endpoint, code_file):
        result = CliRunner().invoke(cli, [str(code_file)], env=ENV)
        assert result.exit_code != 0

    def it_reports_a_failing_endpoint_as_an_error(embeddings_endpoint, code_file):
        embeddings_endpoint.post.return_value.raise_for_status.side_effect = RuntimeError("boom")
        result = CliRunner().invoke(cli, [str(code_file), "--model", "m"], env=ENV)
        assert result.exit_code != 0
        assert "boom" in result.output
