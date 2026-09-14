from click.testing import CliRunner

from template_viewer.cli import cli


def describe_cli():
    def it_prints_html_to_stdout_by_default(sample_transcript):
        result = CliRunner().invoke(cli, [str(sample_transcript)])
        assert result.exit_code == 0
        assert result.output.startswith("<!DOCTYPE html>")
        assert "</html>" in result.output

    def it_writes_html_to_the_output_file(sample_transcript, tmp_path):
        out = tmp_path / "page.html"
        result = CliRunner().invoke(cli, [str(sample_transcript), "--output", str(out)])
        assert result.exit_code == 0
        assert result.output.strip() == str(out)
        body = out.read_text(encoding="utf-8")
        assert body.startswith("<!DOCTYPE html>")
        assert "reference_implementation" in body

    def it_accepts_a_directory_of_transcripts(sample_directory):
        result = CliRunner().invoke(cli, [str(sample_directory)])
        assert result.exit_code == 0
        assert "reference_implementation" in result.output

    def it_uses_a_custom_title(sample_transcript):
        result = CliRunner().invoke(
            cli, [str(sample_transcript), "--title", "Custom Title"]
        )
        assert result.exit_code == 0
        assert "<title>Custom Title</title>" in result.output

    def it_errors_when_the_path_does_not_exist(tmp_path):
        result = CliRunner().invoke(cli, [str(tmp_path / "missing.jsonl")])
        assert result.exit_code != 0

    def it_renders_every_record_type_without_any_unknown(sample_transcript):
        result = CliRunner().invoke(cli, [str(sample_transcript)])
        assert result.exit_code == 0
        assert "type-unknown" not in result.output
        assert "unknown" not in result.output

    def it_embeds_records_json_for_the_modal(sample_transcript):
        result = CliRunner().invoke(cli, [str(sample_transcript)])
        assert '<script type="application/json" id="records">' in result.output
        assert "modal" in result.output

    def it_has_an_eye_button_on_every_row(sample_transcript):
        result = CliRunner().invoke(cli, [str(sample_transcript)])
        # The fixture has 21 records (including one raw line).
        assert result.output.count('class="eye"') == 21
