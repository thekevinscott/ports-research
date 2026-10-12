import json
from pathlib import Path
from unittest.mock import ANY, patch

import pytest

from judge.run_judge import run_judge

RUBRICS = Path(__file__).resolve().parents[2] / "rubrics"
ITEMS = [
    {"id": "item-0000000a", "content": "content a", "entry": {"rubric": "code", "run": "r1", "baseline": False}},
    {"id": "item-0000000b", "content": "content b", "entry": {"rubric": "code", "run": None, "baseline": True}},
    {"id": "item-0000000c", "content": "content c", "entry": {"rubric": "code", "run": "r2", "baseline": False}},
]


@pytest.fixture
def build_items_function():
    with patch("judge.run_judge.build_items", autospec=True) as m:
        m.return_value = ITEMS
        yield m


@pytest.fixture
def shuffle_items_function():
    with patch("judge.run_judge.shuffle_items", autospec=True) as m:
        m.side_effect = lambda items: list(reversed(items))
        yield m


@pytest.fixture
def clone_reference_function(tmp_path):
    with patch("judge.run_judge.clone_reference", autospec=True) as m:
        m.return_value = tmp_path / "gbnf"
        yield m


@pytest.fixture
def judge_item_function():
    with patch("judge.run_judge.judge_item", autospec=True) as m:
        m.side_effect = lambda prompt, **kwargs: {"verdicts": {"p": prompt[-9:]}, "raw": "{}", "usage": {"output_tokens": 1}, "wall_seconds": 2.5}
        yield m


@pytest.fixture
def find_runs_function():
    with patch("judge.run_judge.find_runs", autospec=True) as m:
        m.return_value = [Path("/runs/r1")]
        yield m


@pytest.fixture
def mocks(build_items_function, shuffle_items_function, clone_reference_function, judge_item_function, find_runs_function):
    return {"build_items": build_items_function, "clone_reference": clone_reference_function, "judge_item": judge_item_function, "find_runs": find_runs_function}


def judgments(out):
    return [json.loads(line) for line in (out / "judgments.jsonl").read_text().splitlines()]


def go(out, **overrides):
    options = {"rubric": "code", "runs": [Path("/runs")], "out": out, "limit": None, "model": "m", "effort": "e", "concurrency": 1}
    run_judge(**{**options, **overrides})


def describe_run_judge():
    def it_prompts_with_the_rubric_verbatim_then_the_item_and_the_rubric_schema(mocks, tmp_path):
        go(tmp_path / "out", limit=1)
        rubric = (RUBRICS / "code.md").read_text()
        schema = json.loads((RUBRICS / "code.schema.json").read_text())
        mocks["judge_item"].assert_called_once_with(f"{rubric}\n---\n\ncontent c", schema=schema, model="m", effort="e")

    def it_writes_one_line_per_item_in_shuffled_order(mocks, tmp_path):
        go(tmp_path / "out")
        assert judgments(tmp_path / "out") == [
            {"id": item_id, "rubric": "code", "model": "m", "effort": "e", "verdicts": {"p": f"content {item_id[-1]}"}, "raw": "{}", "usage": {"output_tokens": 1}, "wall_seconds": 2.5}
            for item_id in ("item-0000000c", "item-0000000b", "item-0000000a")
        ]

    def it_writes_a_private_manifest_with_each_items_entry_and_prompt_size(mocks, tmp_path):
        go(tmp_path / "out")
        manifest = json.loads((tmp_path / "out" / "manifest.json").read_text())
        chars = len((RUBRICS / "code.md").read_text()) + len("\n---\n\ncontent a")
        assert manifest["item-0000000a"] == {"rubric": "code", "run": "r1", "baseline": False, "prompt_chars": chars, "tokens_estimate": chars // 4}
        assert set(manifest) == {item["id"] for item in ITEMS}

    def it_keeps_the_entries_of_a_manifest_already_in_out(mocks, tmp_path):
        (tmp_path / "out").mkdir()
        (tmp_path / "out" / "manifest.json").write_text(json.dumps({"item-ffffffff": {"rubric": "transcript"}}))
        go(tmp_path / "out")
        assert "item-ffffffff" in json.loads((tmp_path / "out" / "manifest.json").read_text())

    def it_skips_items_already_judged(mocks, tmp_path):
        (tmp_path / "out").mkdir()
        (tmp_path / "out" / "judgments.jsonl").write_text(json.dumps({"id": "item-0000000b"}) + "\n")
        go(tmp_path / "out")
        assert [c.args[0][-9:] for c in mocks["judge_item"].call_args_list] == ["content c", "content a"]
        assert len(judgments(tmp_path / "out")) == 3

    def it_limits_to_the_first_items_in_shuffled_order(mocks, tmp_path):
        go(tmp_path / "out", limit=2)
        assert [j["id"] for j in judgments(tmp_path / "out")] == ["item-0000000c", "item-0000000b"]

    def it_clones_the_reference_for_the_code_rubric(mocks, tmp_path):
        go(tmp_path / "out")
        mocks["clone_reference"].assert_called_once()
        mocks["find_runs"].assert_called_once_with([Path("/runs")])
        mocks["build_items"].assert_called_once_with(rubric="code", runs=[Path("/runs/r1")], reference=tmp_path / "gbnf")

    def it_needs_no_reference_for_the_transcript_rubric(mocks, tmp_path):
        go(tmp_path / "out", rubric="transcript")
        mocks["clone_reference"].assert_not_called()
        mocks["build_items"].assert_called_once_with(rubric="transcript", runs=[Path("/runs/r1")], reference=None)
        mocks["judge_item"].assert_called_with(ANY, schema=json.loads((RUBRICS / "transcript.schema.json").read_text()), model="m", effort="e")

    def it_writes_every_other_item_then_raises_when_one_fails(mocks, tmp_path):
        def judge(prompt, **kwargs):
            if prompt.endswith("content b"):
                raise RuntimeError("overloaded")
            return {"verdicts": {}, "raw": "{}", "usage": None, "wall_seconds": 1.0}

        mocks["judge_item"].side_effect = judge
        with pytest.raises(RuntimeError, match="item-0000000b"):
            go(tmp_path / "out", concurrency=2)
        assert sorted(j["id"] for j in judgments(tmp_path / "out")) == ["item-0000000a", "item-0000000c"]
