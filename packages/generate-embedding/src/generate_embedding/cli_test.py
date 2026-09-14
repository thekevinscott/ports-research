import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from generate_embedding.cli import cli

RESULT = {"model": "m", "dimension": 2, "embedding": [0.1, 0.2]}


@pytest.fixture
def click():
    with patch("generate_embedding.cli.click") as mock_click:
        # The command wraps any failure in ClickException, so calling it has to
        # produce something `raise` accepts.
        mock_click.ClickException.side_effect = RuntimeError
        yield mock_click


@pytest.fixture
def embed_file():
    with patch("generate_embedding.cli.embed_file", return_value=RESULT) as mock_embed_file:
        yield mock_embed_file


@pytest.fixture
def write_vector():
    with patch("generate_embedding.cli.write_vector") as mock_write_vector:
        yield mock_write_vector


@pytest.fixture
def settings():
    with patch("generate_embedding.cli.Settings") as mock_settings:
        mock_settings.return_value.base_url = "http://host/v1"
        mock_settings.return_value.api_key = None
        yield mock_settings


def describe_cli():
    def it_embeds_the_path_against_the_configured_base_url(
        click, embed_file, write_vector, settings
    ):
        cli.callback(Path("add.py"), "m", None)
        embed_file.assert_called_once_with(
            Path("add.py"), model="m", base_url="http://host/v1", api_key=None
        )

    def it_unwraps_the_api_key_from_settings(click, embed_file, write_vector, settings):
        settings.return_value.api_key = MagicMock()
        settings.return_value.api_key.get_secret_value.return_value = "sk"
        cli.callback(Path("add.py"), "m", None)
        assert embed_file.call_args.kwargs["api_key"] == "sk"

    def it_prints_the_result_as_json_without_an_output_path(
        click, embed_file, write_vector, settings
    ):
        cli.callback(Path("add.py"), "m", None)
        click.echo.assert_called_once_with(json.dumps(RESULT))

    def it_writes_the_vector_to_the_output_path(click, embed_file, write_vector, settings):
        cli.callback(Path("add.py"), "m", Path("vec.npy"))
        write_vector.assert_called_once_with(Path("vec.npy"), [0.1, 0.2])

    def it_prints_the_output_path_instead_of_the_json(click, embed_file, write_vector, settings):
        cli.callback(Path("add.py"), "m", Path("vec.npy"))
        click.echo.assert_called_once_with("vec.npy")

    def it_wraps_a_failure_as_a_click_exception(click, embed_file, write_vector, settings):
        embed_file.side_effect = ValueError("boom")
        with pytest.raises(RuntimeError):
            cli.callback(Path("add.py"), "m", None)
        click.ClickException.assert_called_once_with("boom")
