import json
from pathlib import Path
from unittest.mock import patch

import pytest

from walkthroughs.reference_lines import reference_lines

SIMILARITY = {"name": "fake", "threshold": 0.8, "score": None, "embeddings": None}


@pytest.fixture
def clone_reference(tmp_path):
    with patch("walkthroughs.reference_lines.clone_reference", return_value=tmp_path / "gbnf") as m:
        yield m


@pytest.fixture
def write_walkthrough():
    def write(implementation, *, language, out, model, effort, tag):
        path = out / f"{implementation.name}-{tag}.json"
        path.write_text(json.dumps({"walkthrough": {"from": f"{implementation.name}-{language}-{tag}"}}))
        return path

    with patch("walkthroughs.reference_lines.write_walkthrough", side_effect=write) as m:
        yield m


@pytest.fixture
def compare_walkthroughs():
    with patch("walkthroughs.reference_lines.compare_walkthroughs", side_effect=lambda r, p, s: {"pair": [r["from"], p["from"]]}) as m:
        yield m


@pytest.fixture(autouse=True)
def sweep_thresholds():
    with patch("walkthroughs.reference_lines.sweep_thresholds", side_effect=lambda r, p, s: [r["from"], p["from"]]) as m:
        yield m


def describe_reference_lines():
    def it_explains_each_pinned_reference_twice(tmp_path, clone_reference, write_walkthrough, compare_walkthroughs):
        reference_lines(out=tmp_path / "out", similarity=SIMILARITY, model="m", effort="e")
        calls = sorted((c.args[0], c.kwargs["language"], c.kwargs["tag"], c.kwargs["model"], c.kwargs["effort"]) for c in write_walkthrough.call_args_list)
        assert calls == [
            (tmp_path / "gbnf" / "javascript", "typescript", "a", "m", "e"),
            (tmp_path / "gbnf" / "javascript", "typescript", "b", "m", "e"),
            (tmp_path / "gbnf" / "python", "python", "a", "m", "e"),
            (tmp_path / "gbnf" / "python", "python", "b", "m", "e"),
        ]

    def it_compares_each_reference_with_itself_and_the_two_with_each_other(tmp_path, clone_reference, write_walkthrough, compare_walkthroughs, sweep_thresholds):
        lines = reference_lines(out=tmp_path / "out", similarity=SIMILARITY, model="m", effort="e")
        assert lines["noise_floor"] == {
            "python": {"pair": ["python-python-a", "python-python-b"], "sweep": ["python-python-a", "python-python-b"]},
            "javascript": {"pair": ["javascript-typescript-a", "javascript-typescript-b"], "sweep": ["javascript-typescript-a", "javascript-typescript-b"]},
        }
        assert lines["baseline"] == {
            "python_to_javascript": {"pair": ["python-python-a", "javascript-typescript-a"], "sweep": ["python-python-a", "javascript-typescript-a"]},
            "javascript_to_python": {"pair": ["javascript-typescript-a", "python-python-a"], "sweep": ["javascript-typescript-a", "python-python-a"]},
        }
        assert lines["walkthroughs"] == {"python": {"a": "python-a.json", "b": "python-b.json"}, "javascript": {"a": "javascript-a.json", "b": "javascript-b.json"}}
        assert all(c.args[2] is SIMILARITY for c in compare_walkthroughs.call_args_list + sweep_thresholds.call_args_list)

    def it_writes_the_lines_to_reference_lines_json(tmp_path, clone_reference, write_walkthrough, compare_walkthroughs):
        lines = reference_lines(out=tmp_path / "out", similarity=SIMILARITY, model="m", effort="e")
        assert json.loads(Path(tmp_path / "out" / "reference-lines.json").read_text()) == lines
