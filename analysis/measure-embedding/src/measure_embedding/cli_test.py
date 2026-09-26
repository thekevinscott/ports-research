import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from measure_embedding.cli import cli

EMBED_REPORT = {"language": "python", "target": "/t", "model": "m", "dims": 3, "files": ["a.py"], "embedded": 1, "skipped": 0}
COMPARE_REPORT = {
    "mean_cosine_distance": 0.1,
    "mean_nearest_file_distance": 0.2,
    "chamfer_distance": 0.15,
    "chamfer_a_to_b": 0.2,
    "chamfer_b_to_a": 0.1,
    "file_count_a": 2,
    "file_count_b": 1,
}


@pytest.fixture
def embed_codebase_function():
    with patch("measure_embedding.cli.embed_codebase", autospec=True) as m:
        m.return_value = EMBED_REPORT
        yield m


@pytest.fixture
def compare_embeddings_function():
    with patch("measure_embedding.cli.compare_embeddings", autospec=True) as m:
        m.return_value = COMPARE_REPORT
        yield m


@pytest.fixture
def target(tmp_path):
    directory = tmp_path / "ported_implementation"
    directory.mkdir()
    return directory


@pytest.fixture
def out(tmp_path):
    return tmp_path / "out"


def invoke_embed(target, out, *args):
    return CliRunner().invoke(
        cli, ["embed", "--language", "python", "--target", str(target), "--out", str(out), "--model", "m", *args]
    )


def describe_embed():
    def it_requires_a_language(embed_codebase_function, target, out):
        result = CliRunner().invoke(cli, ["embed", "--target", str(target), "--out", str(out), "--model", "m"])
        assert result.exit_code != 0
        assert "--language" in result.output

    def it_rejects_an_unsupported_language(embed_codebase_function, target, out):
        result = CliRunner().invoke(
            cli, ["embed", "--language", "rust", "--target", str(target), "--out", str(out), "--model", "m"]
        )
        assert result.exit_code != 0
        embed_codebase_function.assert_not_called()

    def it_rejects_a_target_that_does_not_exist(embed_codebase_function, tmp_path, out):
        result = invoke_embed(tmp_path / "nowhere", out)
        assert result.exit_code != 0
        embed_codebase_function.assert_not_called()

    def it_requires_out(embed_codebase_function, target):
        result = CliRunner().invoke(cli, ["embed", "--language", "python", "--target", str(target), "--model", "m"])
        assert result.exit_code != 0
        assert "--out" in result.output

    def it_requires_a_model(embed_codebase_function, target, out):
        result = CliRunner().invoke(cli, ["embed", "--language", "python", "--target", str(target), "--out", str(out)])
        assert result.exit_code != 0
        assert "--model" in result.output

    def it_forwards_language_target_out_and_model(embed_codebase_function, target, out):
        invoke_embed(target, out)
        kwargs = embed_codebase_function.call_args.kwargs
        assert (kwargs["language"], kwargs["target"], kwargs["out"], kwargs["model"]) == ("python", target, out, "m")

    def it_forwards_no_excludes_by_default(embed_codebase_function, target, out):
        invoke_embed(target, out)
        assert embed_codebase_function.call_args.kwargs["exclude"] == []

    def it_forwards_every_exclude_in_order(embed_codebase_function, target, out):
        invoke_embed(target, out, "--exclude", "*_test.py", "--exclude", "build")
        assert embed_codebase_function.call_args.kwargs["exclude"] == ["*_test.py", "build"]

    def it_does_not_strip_comments_by_default(embed_codebase_function, target, out):
        invoke_embed(target, out)
        assert embed_codebase_function.call_args.kwargs["strip_comments"] is False

    def it_forwards_strip_comments_when_the_flag_is_set(embed_codebase_function, target, out):
        invoke_embed(target, out, "--strip-comments")
        assert embed_codebase_function.call_args.kwargs["strip_comments"] is True

    def it_echoes_the_report_as_json_and_exits_zero(embed_codebase_function, target, out):
        result = invoke_embed(target, out)
        assert result.exit_code == 0
        assert json.loads(result.output) == EMBED_REPORT

    def it_renders_errors_as_click_errors(embed_codebase_function, target, out):
        embed_codebase_function.side_effect = FileNotFoundError("no python source")
        result = invoke_embed(target, out)
        assert result.exit_code != 0
        assert "no python source" in result.output


def describe_compare():
    def it_requires_both_directories(compare_embeddings_function, target):
        result = CliRunner().invoke(cli, ["compare", "--a", str(target)])
        assert result.exit_code != 0
        assert "--b" in result.output

    def it_rejects_a_directory_that_does_not_exist(compare_embeddings_function, target, tmp_path):
        result = CliRunner().invoke(cli, ["compare", "--a", str(target), "--b", str(tmp_path / "nowhere")])
        assert result.exit_code != 0
        compare_embeddings_function.assert_not_called()

    def it_forwards_a_and_b(compare_embeddings_function, target):
        CliRunner().invoke(cli, ["compare", "--a", str(target), "--b", str(target)])
        assert compare_embeddings_function.call_args.kwargs == {"a": target, "b": target}

    def it_echoes_the_report_as_json_and_exits_zero(compare_embeddings_function, target):
        result = CliRunner().invoke(cli, ["compare", "--a", str(target), "--b", str(target)])
        assert result.exit_code == 0
        assert json.loads(result.output) == COMPARE_REPORT

    def it_renders_errors_as_click_errors(compare_embeddings_function, target):
        compare_embeddings_function.side_effect = ValueError("dims mismatch")
        result = CliRunner().invoke(cli, ["compare", "--a", str(target), "--b", str(target)])
        assert result.exit_code != 0
        assert "dims mismatch" in result.output
