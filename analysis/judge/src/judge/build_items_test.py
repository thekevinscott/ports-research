import json
from pathlib import Path
from unittest.mock import patch

import pytest

from judge.build_items import build_items

FLAGS = ("include_unit_tests", "include_source_integration_tests", "include_target_integration_tests")


@pytest.fixture
def code_item_function():
    with patch("judge.build_items.code_item", autospec=True) as m:
        m.side_effect = lambda a, b: f"{a} | {b}"
        yield m


@pytest.fixture
def transcript_item_function():
    with patch("judge.build_items.transcript_item", autospec=True) as m:
        m.side_effect = lambda files: " ".join(str(f) for f in files)
        yield m


def run(root, name, source, flags=(True, False, True)):
    path = root / name
    (path / "transcript" / ".claude" / "projects" / "-target").mkdir(parents=True)
    (path / "transcript" / ".claude" / "projects" / "-target" / "b.jsonl").write_text("")
    (path / "transcript" / ".claude" / "projects" / "-target" / "a.jsonl").write_text("")
    condition = {"source_language": source, "target_language": {"python": "javascript", "javascript": "python"}[source], **dict(zip(FLAGS, flags))}
    (path / "manifest.json").write_text(json.dumps({"exit_code": 0, "condition": condition}))
    return path


def describe_build_items():
    def describe_code():
        def it_builds_the_human_pair_both_ways_then_each_run_against_its_source(code_item_function, tmp_path):
            reference = tmp_path / "gbnf"
            runs = [run(tmp_path, "r1", "python"), run(tmp_path, "r2", "javascript")]
            build_items(rubric="code", runs=runs, reference=reference)
            assert [c.args for c in code_item_function.call_args_list] == [
                (reference / "python", reference / "javascript"),
                (reference / "javascript", reference / "python"),
                (reference / "python", runs[0] / "ported_implementation"),
                (reference / "javascript", runs[1] / "ported_implementation"),
            ]

        def it_marks_the_two_baseline_items_and_maps_the_rest_to_their_runs(code_item_function, tmp_path):
            items = build_items(rubric="code", runs=[run(tmp_path, "r1", "python", (True, False, True))], reference=tmp_path)
            entries = [item["entry"] for item in items]
            assert entries == [
                {"rubric": "code", "run": None, "baseline": True, "source_language": "python", "target_language": "javascript", **dict.fromkeys(FLAGS)},
                {"rubric": "code", "run": None, "baseline": True, "source_language": "javascript", "target_language": "python", **dict.fromkeys(FLAGS)},
                {"rubric": "code", "run": "r1", "baseline": False, "source_language": "python", "target_language": "javascript", "include_unit_tests": True, "include_source_integration_tests": False, "include_target_integration_tests": True},
            ]

        def it_ids_each_item_from_its_content(code_item_function, tmp_path):
            items = build_items(rubric="code", runs=[], reference=tmp_path)
            assert [item["content"] for item in items] == [f"{tmp_path / 'python'} | {tmp_path / 'javascript'}", f"{tmp_path / 'javascript'} | {tmp_path / 'python'}"]
            assert items[0]["id"] != items[1]["id"]
            assert all(item["id"].startswith("item-") for item in items)

    def describe_transcript():
        def it_builds_one_item_per_run_from_its_transcripts_in_name_order_and_no_baseline(transcript_item_function, tmp_path):
            r1 = run(tmp_path, "r1", "javascript")
            items = build_items(rubric="transcript", runs=[r1], reference=None)
            directory = r1 / "transcript" / ".claude" / "projects" / "-target"
            transcript_item_function.assert_called_once_with([directory / "a.jsonl", directory / "b.jsonl"])
            assert [item["entry"]["run"] for item in items] == ["r1"]
            assert items[0]["entry"]["baseline"] is False
            assert items[0]["entry"]["rubric"] == "transcript"

    def it_rejects_an_unknown_rubric(tmp_path):
        with pytest.raises(ValueError, match="rubric"):
            build_items(rubric="vibes", runs=[], reference=Path(tmp_path))
