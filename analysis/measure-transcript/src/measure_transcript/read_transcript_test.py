import json

import pytest

from measure_transcript.read_transcript import read_transcript

USAGE = {"input_tokens": 1, "output_tokens": 2, "cache_read_input_tokens": 3, "cache_creation_input_tokens": 4}


def assistant(message_id, time, blocks, cwd="/target"):
    return {
        "type": "assistant",
        "timestamp": time,
        "cwd": cwd,
        "message": {"id": message_id, "content": blocks, "usage": USAGE},
    }


def tool_use(use_id, name, **tool_input):
    return {"type": "tool_use", "id": use_id, "name": name, "input": tool_input}


def tool_result(use_id, time, content):
    return {"type": "user", "timestamp": time, "message": {"content": [{"type": "tool_result", "tool_use_id": use_id, "content": content}]}}


def write(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in records))


@pytest.fixture
def session(tmp_path):
    return tmp_path / "transcript" / ".claude" / "projects" / "-target" / "s.jsonl"


def describe_read_transcript():
    def it_numbers_turns_by_message_id_from_one(tmp_path, session):
        write(session, [
            assistant("m1", "2026-01-01T00:00:01Z", [{"type": "text", "text": "hi"}]),
            assistant("m1", "2026-01-01T00:00:02Z", [tool_use("u1", "Bash", command="ls")]),
            assistant("m2", "2026-01-01T00:00:03Z", [tool_use("u2", "Read", file_path="/a")]),
        ])
        transcript = read_transcript(tmp_path)
        assert transcript["usage"] == [USAGE, USAGE]
        assert [(c["turn"], c["name"]) for c in transcript["calls"]] == [(1, "Bash"), (2, "Read")]

    def it_attaches_the_cwd_and_the_result_text(tmp_path, session):
        write(session, [
            assistant("m1", "2026-01-01T00:00:01Z", [tool_use("u1", "Bash", command="ls"), tool_use("u2", "Bash", command="pwd")], cwd="/target/src"),
            tool_result("u1", "2026-01-01T00:00:02Z", "a\nb"),
            tool_result("u2", "2026-01-01T00:00:03Z", [{"type": "text", "text": "/target"}, {"type": "text", "text": "/src"}]),
        ])
        calls = read_transcript(tmp_path)["calls"]
        assert [(c["input"], c["cwd"], c["result"]) for c in calls] == [
            ({"command": "ls"}, "/target/src", "a\nb"),
            ({"command": "pwd"}, "/target/src", "/target\n/src"),
        ]

    def it_leaves_the_result_empty_when_none_came_back(tmp_path, session):
        write(session, [assistant("m1", "2026-01-01T00:00:01Z", [tool_use("u1", "Bash", command="ls")])])
        assert read_transcript(tmp_path)["calls"][0]["result"] == ""

    def it_merges_subagent_transcripts_by_time(tmp_path, session):
        write(session, [
            assistant("m1", "2026-01-01T00:00:01Z", [tool_use("u1", "Agent", prompt="x")]),
            assistant("m3", "2026-01-01T00:00:05Z", [tool_use("u3", "Bash", command="ls")]),
        ])
        write(session.parent / "s" / "subagents" / "agent-a.jsonl", [
            assistant("m2", "2026-01-01T00:00:03Z", [tool_use("u2", "Read", file_path="/a")]),
        ])
        assert [(c["turn"], c["name"]) for c in read_transcript(tmp_path)["calls"]] == [(1, "Agent"), (2, "Read"), (3, "Bash")]

    def it_skips_lines_that_are_not_json(tmp_path, session):
        session.parent.mkdir(parents=True)
        session.write_text("not json\n" + json.dumps(assistant("m1", "2026-01-01T00:00:01Z", [])) + "\n")
        assert len(read_transcript(tmp_path)["usage"]) == 1

    def it_raises_when_the_run_has_no_transcript(tmp_path):
        with pytest.raises(FileNotFoundError, match="no transcript"):
            read_transcript(tmp_path)
