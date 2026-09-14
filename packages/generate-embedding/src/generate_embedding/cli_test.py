import json
from unittest.mock import patch

import numpy as np
from click.testing import CliRunner

from generate_embedding.cli import cli

ENV = {"GENERATE_EMBEDDING_BASE_URL": "http://localhost:8080/v1"}


def describe_cli():
    def it_errors_when_the_path_does_not_exist(tmp_path):
        result = CliRunner().invoke(
            cli, [str(tmp_path / "missing.py"), "--model", "m"], env=ENV
        )
        assert result.exit_code != 0

    def it_errors_when_model_is_missing(tmp_path):
        path = tmp_path / "add.py"
        path.write_text("x = 1")
        result = CliRunner().invoke(cli, [str(path)], env=ENV)
        assert result.exit_code != 0

    def it_prints_the_embedding_as_json_by_default(tmp_path):
        path = tmp_path / "add.py"
        path.write_text("x = 1")
        canned = {"model": "m", "dimension": 2, "embedding": [0.1, 0.2]}
        with patch("generate_embedding.cli.embed_file", return_value=canned) as mock_embed_file:
            result = CliRunner().invoke(cli, [str(path), "--model", "m"], env=ENV)
        assert result.exit_code == 0
        assert json.loads(result.output) == canned
        mock_embed_file.assert_called_once_with(
            path, model="m", base_url="http://localhost:8080/v1", api_key=None
        )

    def it_writes_a_npy_file_when_output_is_given(tmp_path):
        path = tmp_path / "add.py"
        path.write_text("x = 1")
        output = tmp_path / "vec.npy"
        canned = {"model": "m", "dimension": 3, "embedding": [0.1, 0.2, 0.3]}
        with patch("generate_embedding.cli.embed_file", return_value=canned):
            result = CliRunner().invoke(
                cli, [str(path), "--model", "m", "--output", str(output)], env=ENV
            )
        assert result.exit_code == 0
        assert result.output.strip() == str(output)
        loaded = np.load(output)
        assert loaded.dtype == np.float32
        np.testing.assert_allclose(loaded, [0.1, 0.2, 0.3], rtol=1e-6)

    def it_passes_the_api_key_from_settings(tmp_path):
        path = tmp_path / "add.py"
        path.write_text("x = 1")
        canned = {"model": "m", "dimension": 1, "embedding": [0.1]}
        env = {**ENV, "GENERATE_EMBEDDING_API_KEY": "sk-test"}
        with patch("generate_embedding.cli.embed_file", return_value=canned) as mock_embed_file:
            CliRunner().invoke(cli, [str(path), "--model", "m"], env=env)
        mock_embed_file.assert_called_once_with(
            path, model="m", base_url="http://localhost:8080/v1", api_key="sk-test"
        )
