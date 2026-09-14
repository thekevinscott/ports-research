import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from contamination_probe.cli import cli


@pytest.fixture
def perturb_reference_tree_function():
    with patch("contamination_probe.cli.perturb_reference_tree", autospec=True) as m:
        m.return_value = "lattice"
        yield m


@pytest.fixture
def source(tmp_path):
    directory = tmp_path / "source"
    directory.mkdir()
    return directory


def invoke(source, output, *args):
    return CliRunner().invoke(
        cli,
        ["--source", str(source), "--output", str(output), "--library-name", "gbnf", *args],
    )


def describe_cli():
    def it_requires_a_source(perturb_reference_tree_function, tmp_path):
        result = CliRunner().invoke(
            cli, ["--output", str(tmp_path / "out"), "--library-name", "gbnf"]
        )
        assert result.exit_code != 0
        assert "--source" in result.output

    def it_rejects_a_source_that_does_not_exist(perturb_reference_tree_function, tmp_path):
        result = invoke(tmp_path / "nowhere", tmp_path / "out")
        assert result.exit_code != 0
        perturb_reference_tree_function.assert_not_called()

    def it_requires_an_output(perturb_reference_tree_function, source):
        result = CliRunner().invoke(
            cli, ["--source", str(source), "--library-name", "gbnf"]
        )
        assert result.exit_code != 0
        assert "--output" in result.output

    def it_requires_a_library_name(perturb_reference_tree_function, source, tmp_path):
        result = CliRunner().invoke(
            cli, ["--source", str(source), "--output", str(tmp_path / "out")]
        )
        assert result.exit_code != 0
        assert "--library-name" in result.output

    def it_defaults_the_seed_to_zero(perturb_reference_tree_function, source, tmp_path):
        invoke(source, tmp_path / "out")
        assert perturb_reference_tree_function.call_args.kwargs["seed"] == 0

    def it_forwards_a_provided_seed(perturb_reference_tree_function, source, tmp_path):
        invoke(source, tmp_path / "out", "--seed", "7")
        assert perturb_reference_tree_function.call_args.kwargs["seed"] == 7

    def it_forwards_source_output_and_library_name(
        perturb_reference_tree_function, source, tmp_path
    ):
        output = tmp_path / "out"
        invoke(source, output)
        args = perturb_reference_tree_function.call_args
        assert args.args == (source, output)
        assert args.kwargs["library_name"] == "gbnf"

    def it_echoes_the_new_library_name_as_json(
        perturb_reference_tree_function, source, tmp_path
    ):
        result = invoke(source, tmp_path / "out")
        assert json.loads(result.output)["library_name"] == "lattice"

    def it_exits_zero_on_success(perturb_reference_tree_function, source, tmp_path):
        result = invoke(source, tmp_path / "out")
        assert result.exit_code == 0

    def it_renders_errors_as_click_errors(perturb_reference_tree_function, source, tmp_path):
        perturb_reference_tree_function.side_effect = FileNotFoundError("no such directory")
        result = invoke(source, tmp_path / "out")
        assert result.exit_code != 0
        assert "no such directory" in result.output
