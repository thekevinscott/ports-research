import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from walkthroughs.cli import cli

SIMILARITY = {"name": "fake", "threshold": 0.8, "score": None, "embeddings": None}


@pytest.fixture
def write_walkthrough():
    with patch("walkthroughs.cli.write_walkthrough", return_value=Path("/out/abc.json")) as m:
        yield m


@pytest.fixture
def pick_similarity():
    with patch("walkthroughs.cli.pick_similarity", return_value=SIMILARITY) as m:
        yield m


@pytest.fixture
def compare_walkthroughs():
    with patch("walkthroughs.cli.compare_walkthroughs", return_value={"mean_coverage": 0.5}) as m:
        yield m


@pytest.fixture(autouse=True)
def sweep_thresholds():
    with patch("walkthroughs.cli.sweep_thresholds", return_value=[{"threshold": 0.7}]) as m:
        yield m


@pytest.fixture
def reference_lines():
    with patch("walkthroughs.cli.reference_lines", return_value={"baseline": {}}) as m:
        yield m


def invoke(*args):
    return CliRunner().invoke(cli, [str(a) for a in args])


def describe_write():
    def it_writes_with_opus_at_high_effort_by_default_and_prints_the_path(tmp_path, write_walkthrough):
        result = invoke("write", "--implementation", tmp_path, "--language", "python", "--out", tmp_path / "out")
        assert result.exit_code == 0, result.output
        write_walkthrough.assert_called_once_with(tmp_path, language="python", out=tmp_path / "out", model="claude-opus-5-5", effort="high", tag="")
        assert result.output == "/out/abc.json\n"

    def it_passes_model_effort_and_tag(tmp_path, write_walkthrough):
        invoke("write", "--implementation", tmp_path, "--language", "typescript", "--out", tmp_path, "--model", "m", "--effort", "e", "--tag", "a")
        assert write_walkthrough.call_args.kwargs == {"language": "typescript", "out": tmp_path, "model": "m", "effort": "e", "tag": "a"}


def describe_compare():
    def it_compares_the_two_walkthroughs_and_prints_json_with_the_threshold_sweep(tmp_path, pick_similarity, compare_walkthroughs, sweep_thresholds):
        (tmp_path / "r.json").write_text(json.dumps({"walkthrough": {"entry_points": ["r"]}}))
        (tmp_path / "p.json").write_text(json.dumps({"walkthrough": {"entry_points": ["p"]}}))
        result = invoke("compare", "--reference", tmp_path / "r.json", "--port", tmp_path / "p.json", "--embeddings-url", "http://host/v1")
        assert result.exit_code == 0, result.output
        pick_similarity.assert_called_once_with(url="http://host/v1", no_embeddings=False, threshold=None)
        compare_walkthroughs.assert_called_once_with({"entry_points": ["r"]}, {"entry_points": ["p"]}, SIMILARITY)
        sweep_thresholds.assert_called_once_with({"entry_points": ["r"]}, {"entry_points": ["p"]}, SIMILARITY)
        assert json.loads(result.output) == {"reference": str(tmp_path / "r.json"), "port": str(tmp_path / "p.json"), "mean_coverage": 0.5, "sweep": [{"threshold": 0.7}]}

    def it_passes_the_fallback_and_threshold(tmp_path, pick_similarity, compare_walkthroughs):
        for name in ("r.json", "p.json"):
            (tmp_path / name).write_text(json.dumps({"walkthrough": {}}))
        invoke("compare", "--reference", tmp_path / "r.json", "--port", tmp_path / "p.json", "--no-embeddings", "--threshold", "0.6")
        pick_similarity.assert_called_once_with(url=None, no_embeddings=True, threshold=0.6)

    def it_fails_cleanly_without_a_url_or_the_fallback(tmp_path, pick_similarity, compare_walkthroughs):
        pick_similarity.side_effect = ValueError("pass --embeddings-url or --no-embeddings")
        for name in ("r.json", "p.json"):
            (tmp_path / name).write_text(json.dumps({"walkthrough": {}}))
        result = invoke("compare", "--reference", tmp_path / "r.json", "--port", tmp_path / "p.json")
        assert result.exit_code != 0
        assert "--embeddings-url" in result.output


def describe_reference_lines():
    def it_writes_the_reference_lines_and_prints_them(tmp_path, pick_similarity, reference_lines):
        result = invoke("reference-lines", "--out", tmp_path, "--embeddings-url", "http://host/v1")
        assert result.exit_code == 0, result.output
        reference_lines.assert_called_once_with(out=tmp_path, similarity=SIMILARITY, model="claude-opus-5-5", effort="high")
        assert json.loads(result.output) == {"baseline": {}}
