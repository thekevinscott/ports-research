import json
from unittest.mock import patch

import pytest

from walkthroughs.write_walkthrough import SCHEMA, write_walkthrough

WALKTHROUGH = {"entry_points": [{"name": "parse", "happy_path": ["s"], "error_paths": [], "invariants": []}]}


@pytest.fixture
def build_prompt():
    with patch("walkthroughs.write_walkthrough.build_prompt", return_value=("the prompt", ["a.py"])) as m:
        yield m


@pytest.fixture
def judge_item():
    judged = {"verdicts": WALKTHROUGH, "raw": "{}", "usage": {"output_tokens": 9}, "wall_seconds": 1.5}
    with patch("walkthroughs.write_walkthrough.judge_item", return_value=judged) as m:
        yield m


@pytest.fixture
def content_hash():
    with patch("walkthroughs.write_walkthrough.content_hash", return_value="0123456789abcdef") as m:
        yield m


def write(tmp_path, tag=""):
    return write_walkthrough(tmp_path / "impl", language="python", out=tmp_path / "out", model="m", effort="e", tag=tag)


def describe_write_walkthrough():
    def it_writes_the_walkthrough_with_its_call_record_under_the_content_hash(tmp_path, build_prompt, judge_item, content_hash):
        path = write(tmp_path, tag="a")
        assert path == tmp_path / "out" / "0123456789abcdef.json"
        assert json.loads(path.read_text()) == {
            "implementation": str(tmp_path / "impl"),
            "language": "python",
            "tag": "a",
            "model": "m",
            "effort": "e",
            "files": ["a.py"],
            "prompt_chars": len("the prompt"),
            "walkthrough": WALKTHROUGH,
            "raw": "{}",
            "usage": {"output_tokens": 9},
            "wall_seconds": 1.5,
        }
        content_hash.assert_called_once_with("the prompt", "m", "e", "a")

    def it_calls_claude_once_on_the_prompt_with_the_walkthrough_schema(tmp_path, build_prompt, judge_item, content_hash):
        write(tmp_path)
        judge_item.assert_called_once_with("the prompt", schema=SCHEMA, model="m", effort="e")
        build_prompt.assert_called_once_with(tmp_path / "impl", "python")

    def it_skips_the_call_when_the_hash_is_already_written(tmp_path, build_prompt, judge_item, content_hash):
        (tmp_path / "out").mkdir()
        (tmp_path / "out" / "0123456789abcdef.json").write_text("{}")
        assert write(tmp_path) == tmp_path / "out" / "0123456789abcdef.json"
        judge_item.assert_not_called()
