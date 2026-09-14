import pytest

from template_viewer.cli import cli


@pytest.fixture
def runner():
    from click.testing import CliRunner

    return CliRunner()


def describe_cli_e2e():
    def it_round_trips_a_real_transcript_file(runner, sample_transcript):
        result = runner.invoke(cli, [str(sample_transcript)])
        assert result.exit_code == 0
        assert "<!DOCTYPE html>" in result.output

    def it_renders_every_record_type_in_the_sample_without_unknowns(runner, sample_transcript):
        result = runner.invoke(cli, [str(sample_transcript)])
        assert "type-queue-operation" in result.output
        assert "type-user" in result.output
        assert "type-assistant" in result.output
        assert "type-attachment" in result.output
        assert "type-atis-latch" in result.output
        assert "type-last-prompt" in result.output
        # The deliberately malformed line is kept visible, not dropped.
        assert "type-raw" in result.output
        # No record falls through to an unknown row.
        assert "type-unknown" not in result.output
        assert ">unknown<" not in result.output
