import json

from judge.transcript_item import transcript_item


def assistant(*blocks):
    return {"type": "assistant", "message": {"role": "assistant", "content": list(blocks)}}


def result(text):
    return {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t", "content": text}]}}


def write(path, records):
    path.write_text("".join(json.dumps(record) + "\n" for record in records))
    return path


def describe_transcript_item():
    def it_numbers_text_and_tool_calls_in_order_and_drops_results_thinking_and_the_prompt(tmp_path):
        path = write(tmp_path / "s.jsonl", [
            {"type": "user", "message": {"role": "user", "content": "Port the implementation"}},
            assistant({"type": "thinking", "thinking": "hidden"}),
            assistant({"type": "text", "text": "Reading the source."}),
            assistant({"type": "tool_use", "id": "t", "name": "Bash", "input": {"command": "ls /input"}}),
            result("python/"),
            {"type": "attachment", "attachment": {}},
            assistant({"type": "tool_use", "id": "u", "name": "Read", "input": {"file_path": "/input/python/gbnf/GBNF.py"}}),
        ])
        assert transcript_item([path]) == (
            "[1] text: Reading the source.\n"
            '[2] Bash: {"command": "ls /input"}\n'
            '[3] Read: {"file_path": "/input/python/gbnf/GBNF.py"}\n'
        )

    def it_cuts_tool_input_strings_at_2000_characters_and_says_how_much_was_cut(tmp_path):
        content = "a" * 2000 + "b" * 500
        path = write(tmp_path / "s.jsonl", [
            assistant({"type": "tool_use", "id": "t", "name": "Write", "input": {"file_path": "/target/x.ts", "content": content}}),
        ])
        line = transcript_item([path])
        written = json.loads(line.removeprefix("[1] Write: "))["content"]
        assert written == "a" * 2000 + "[500 more characters cut]"

    def it_keeps_text_whole(tmp_path):
        path = write(tmp_path / "s.jsonl", [assistant({"type": "text", "text": "t" * 3000})])
        assert transcript_item([path]) == "[1] text: " + "t" * 3000 + "\n"

    def it_cuts_strings_nested_in_lists_and_objects(tmp_path):
        path = write(tmp_path / "s.jsonl", [
            assistant({"type": "tool_use", "id": "t", "name": "MultiEdit", "input": {"edits": [{"new_string": "n" * 2001}]}}),
        ])
        edits = json.loads(transcript_item([path]).removeprefix("[1] MultiEdit: "))["edits"]
        assert edits == [{"new_string": "n" * 2000 + "[1 more characters cut]"}]

    def it_continues_numbering_across_files(tmp_path):
        first = write(tmp_path / "a.jsonl", [assistant({"type": "text", "text": "one"})])
        second = write(tmp_path / "b.jsonl", [assistant({"type": "text", "text": "two"})])
        assert transcript_item([first, second]) == "[1] text: one\n[2] text: two\n"
