import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from measure_transcript.cli import cli


@pytest.fixture
def measure_transcript_function():
    with patch("measure_transcript.cli.measure_transcript", autospec=True) as m:
        m.return_value = {"turns": 3}
        yield m


def describe_cli():
    def it_prints_the_measures_of_the_run_as_json(measure_transcript_function, tmp_path):
        result = CliRunner().invoke(cli, ["--run", str(tmp_path)])
        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == {"turns": 3}
        assert measure_transcript_function.call_args.args == (tmp_path.resolve(),)

    @pytest.mark.parametrize("error", [FileNotFoundError("no transcript under x"), ValueError("bad source_language")])
    def it_exits_non_zero_with_the_message(measure_transcript_function, tmp_path, error):
        measure_transcript_function.side_effect = error
        result = CliRunner().invoke(cli, ["--run", str(tmp_path)])
        assert result.exit_code != 0
        assert str(error) in result.output

    def it_requires_an_existing_run_directory(measure_transcript_function, tmp_path):
        result = CliRunner().invoke(cli, ["--run", str(tmp_path / "missing")])
        assert result.exit_code != 0
        measure_transcript_function.assert_not_called()
