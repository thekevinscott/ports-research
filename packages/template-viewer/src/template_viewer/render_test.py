import json
from pathlib import Path

import pytest

from template_viewer.render import render_html, render_transcript


def _records():
    return [
        {
            "type": "queue-operation",
            "operation": "enqueue",
            "content": "Port reference_implementation/ to typescript.",
        },
        {"type": "attachment", "attachment": {"type": "deferred_tools_delta", "addedNames": ["Bash", "Read"], "removedNames": ["Old"]}},
        {"type": "attachment", "attachment": {"type": "agent_listing_delta", "addedTypes": ["main"], "removedTypes": []}},
        {"type": "attachment", "attachment": {"type": "skill_listing", "skillCount": 13}},
        {"type": "attachment", "attachment": {"type": "total_tokens_reminder", "text": "<total_tokens>15000000 tokens left</total_tokens>"}},
        {"type": "attachment", "attachment": {"type": "edited_text_file", "filename": "/workspace/ported.py"}},
        {"type": "attachment", "attachment": {"type": "queued_command", "commandMode": "task-notification"}},
        {"type": "attachment", "attachment": {"type": "read_truncation_notice", "banner": "[Truncated: showing lines 1-1414 of 1753 total.]"}},
        {"type": "attachment", "attachment": {"type": "date_change", "newDate": "2026-09-09"}},
        {"type": "user", "message": {"role": "user", "content": "port it"}},
        {
            "type": "assistant",
            "message": {
                "id": "m1",
                "role": "assistant",
                "model": "claude-opus-5",
                "content": [
                    {"type": "text", "text": "Looking at src/index.ts"},
                    {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "ls"}},
                    {"type": "thinking", "thinking": "need to read it first"},
                ],
                "usage": {"input_tokens": 10, "output_tokens": 5, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 200},
            },
        },
        {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "a\nb\nc"}]}},
        {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t2", "is_error": True, "content": "boom"}]}},
        {"type": "atis-latch", "atis": "", "sessionId": "s1"},
        {"type": "last-prompt", "lastPrompt": "Port it.", "leafUuid": "x"},
        {"type": "queue-operation", "operation": "dequeue"},
        {"type": "raw", "line": "garbage line"},
    ]


def describe_render_html():
    def it_produces_a_complete_html_document():
        out = render_html(_records(), title="t")
        assert out.startswith("<!DOCTYPE html>")
        assert "</html>" in out

    def it_puts_the_title_in_the_header():
        out = render_html(_records(), title="My Transcript")
        assert "<title>My Transcript</title>" in out
        assert "<h1>My Transcript</h1>" in out

    def it_renders_one_row_per_record():
        out = render_html(_records(), title="t")
        # 17 records in _records()
        assert out.count('class="row ') == 17

    def it_renders_no_unknown_rows_for_real_record_types():
        out = render_html(_records(), title="t")
        assert "type-unknown" not in out
        assert "unknown" not in out

    def it_marks_each_row_with_its_type_class():
        out = render_html(_records(), title="t")
        for cls in [
            "type-queue-operation",
            "type-user",
            "type-assistant",
            "type-attachment",
            "type-atis-latch",
            "type-last-prompt",
            "type-raw",
        ]:
            assert cls in out

    def it_shows_a_colored_icon_and_kind_label_per_row():
        out = render_html(_records(), title="t")
        assert 'class="icon"' in out
        assert 'class="kind"' in out
        assert ">prompt<" in out
        assert ">user<" in out
        assert ">assistant<" in out
        assert ">attachment<" in out

    def it_puts_an_eye_button_on_every_row():
        out = render_html(_records(), title="t")
        assert out.count('class="eye"') == 17

    def it_embeds_the_full_records_json_for_the_modal():
        out = render_html(_records(), title="t")
        assert '<script type="application/json" id="records">' in out
        # The first record's prompt text is in the embedded JSON.
        assert "Port reference_implementation/" in out

    def it_escapes_so_model_output_cannot_close_the_script_block():
        records = [{"type": "user", "message": {"content": "</script><script>alert(1)"}}]
        out = render_html(records, title="t")
        assert "</script><script>" not in out
        assert "\\u003c/script>" in out

    def it_sums_usage_across_distinct_message_ids():
        out = render_html(
            [
                {"type": "assistant", "message": {"id": "m1", "usage": {"input_tokens": 10, "output_tokens": 5}}},
                {"type": "assistant", "message": {"id": "m1", "usage": {"input_tokens": 10, "output_tokens": 5}}},
                {"type": "assistant", "message": {"id": "m2", "usage": {"input_tokens": 7, "output_tokens": 3}}},
            ],
            title="t",
        )
        assert "<b>17</b> in" in out
        assert "<b>8</b> out" in out
        assert "<b>2</b> calls" in out

    def it_renders_a_queue_enqueue_as_the_prompt_text():
        out = render_html([{"type": "queue-operation", "operation": "enqueue", "content": "do the thing"}], title="t")
        assert "do the thing" in out

    def it_renders_queue_dequeue_and_remove_compactly():
        out = render_html([{"type": "queue-operation", "operation": "dequeue"}], title="t")
        assert "[queue: dequeue]" in out

    def it_renders_each_attachment_subtype():
        records = [
            {"type": "attachment", "attachment": {"type": "deferred_tools_delta", "addedNames": ["a", "b"], "removedNames": ["c"]}},
            {"type": "attachment", "attachment": {"type": "agent_listing_delta", "addedTypes": ["x"], "removedTypes": []}},
            {"type": "attachment", "attachment": {"type": "skill_listing", "skillCount": 5}},
            {"type": "attachment", "attachment": {"type": "total_tokens_reminder", "text": "<total_tokens>999 tokens left</total_tokens>"}},
            {"type": "attachment", "attachment": {"type": "edited_text_file", "filename": "/x.py"}},
            {"type": "attachment", "attachment": {"type": "queued_command", "commandMode": "task-notification"}},
            {"type": "attachment", "attachment": {"type": "read_truncation_notice", "banner": "[Truncated: short.]"}},
            {"type": "attachment", "attachment": {"type": "date_change", "newDate": "2026-09-09"}},
        ]
        out = render_html(records, title="t")
        assert "deferred_tools_delta +2 -1" in out
        assert "agent_listing_delta +1" in out
        assert "skill_listing (5 skills)" in out
        assert "999 tokens left" in out
        assert "edited_text_file /x.py" in out
        assert "queued_command (task-notification)" in out
        assert "[Truncated: short.]" in out
        assert "date_change → 2026-09-09" in out

    def it_renders_assistant_text_tool_use_and_thinking():
        out = render_html(
            [{"type": "assistant", "message": {"content": [
                {"type": "text", "text": "hello"},
                {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}},
                {"type": "thinking", "thinking": "hmm"},
            ]}}],
            title="t",
        )
        assert "hello" in out
        assert "→ Bash:" in out
        assert "(thinking) hmm" in out

    def it_renders_tool_results_with_id_and_error_flag():
        out = render_html(
            [
                {"type": "user", "message": {"content": [
                    {"type": "tool_result", "tool_use_id": "t1", "content": "ok out"},
                ]}},
                {"type": "user", "message": {"content": [
                    {"type": "tool_result", "tool_use_id": "t2", "is_error": True, "content": "boom"},
                ]}},
            ],
            title="t",
        )
        assert "tool result t1" in out
        assert "tool result t2" in out
        assert "(error)" in out

    def it_keeps_unparseable_lines_visible_as_raw():
        out = render_html([{"type": "raw", "line": "garbage line"}], title="t")
        assert "garbage line" in out
        assert "type-raw" in out

    def it_shows_an_empty_state_when_there_are_no_records():
        out = render_html([], title="t")
        assert "No transcript records." in out


def describe_render_transcript():
    def it_loads_and_renders_a_file(tmp_path: Path):
        path = tmp_path / "s.jsonl"
        path.write_text(
            "\n".join(json.dumps(r) for r in _records()),
            encoding="utf-8",
        )
        out = render_transcript(path)
        assert out.startswith("<!DOCTYPE html>")
        assert "Port reference_implementation/" in out
