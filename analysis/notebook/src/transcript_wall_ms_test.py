import json

from src.transcript_wall_ms import transcript_wall_ms


def write(path, *timestamps, extra=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps({"type": "assistant", "timestamp": t}) for t in timestamps]
    path.write_text("\n".join([*lines, extra]))


def describe_transcript_wall_ms():
    def it_spans_the_first_to_the_last_timestamp_across_every_session_file(tmp_path):
        write(tmp_path / "transcript" / "session.jsonl", "2026-10-12T02:13:10.000Z", "2026-10-12T02:14:10.000Z")
        write(
            tmp_path / "transcript" / ".claude" / "projects" / "-target" / "s" / "subagents" / "agent.jsonl",
            "2026-10-12T02:13:40.000Z",
            "2026-10-12T02:20:10.500Z",
        )
        assert transcript_wall_ms(tmp_path) == 420_500

    def it_skips_lines_that_are_not_json_or_carry_no_timestamp(tmp_path):
        write(tmp_path / "transcript" / "session.jsonl", "2026-10-12T02:13:10Z", "2026-10-12T02:13:20Z", extra='{"type": "summary"}\nnot json')
        assert transcript_wall_ms(tmp_path) == 10_000

    def it_is_none_without_a_timestamp(tmp_path):
        (tmp_path / "transcript").mkdir()
        assert transcript_wall_ms(tmp_path) is None
