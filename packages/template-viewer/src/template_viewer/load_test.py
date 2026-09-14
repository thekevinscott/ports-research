import json
from pathlib import Path

import pytest

from template_viewer.load import load_records


@pytest.fixture
def transcript_file(tmp_path: Path) -> Path:
    path = tmp_path / "session.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps({"type": "system", "subtype": "init", "sessionId": "s1"}),
                json.dumps({"type": "user", "message": {"content": "hi"}}),
                "",
                "not json",
                json.dumps({"type": "assistant", "message": {"id": "m1", "usage": {}}}),
            ]
        ),
        encoding="utf-8",
    )
    return path


def describe_load_records():
    def it_reads_each_json_line_as_a_record(transcript_file):
        records = load_records(transcript_file)
        assert [r["type"] for r in records] == ["system", "user", "raw", "assistant"]

    def it_skips_blank_lines(transcript_file):
        # Four non-blank lines: three JSON records plus one raw line.
        assert len(load_records(transcript_file)) == 4

    def it_keeps_unparseable_lines_as_raw_records(transcript_file):
        raws = [r for r in load_records(transcript_file) if r.get("type") == "raw"]
        assert len(raws) == 1
        assert raws[0]["line"] == "not json"

    def it_reads_every_jsonl_under_a_directory_in_sorted_order(tmp_path):
        root = tmp_path / "transcript" / "-workspace"
        root.mkdir(parents=True)
        (root / "b.jsonl").write_text(json.dumps({"type": "user", "message": {"content": "b"}}))
        (root / "a.jsonl").write_text(json.dumps({"type": "user", "message": {"content": "a"}}))
        records = load_records(tmp_path)
        assert [r["message"]["content"] for r in records] == ["a", "b"]

    def it_returns_empty_for_an_empty_directory(tmp_path):
        assert load_records(tmp_path) == []
