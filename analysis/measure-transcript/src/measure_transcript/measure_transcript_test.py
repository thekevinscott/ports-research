import json

import pytest

from measure_transcript.measure_transcript import measure_transcript

USAGE = {"input_tokens": 1, "output_tokens": 10, "cache_read_input_tokens": 100, "cache_creation_input_tokens": 1000}


def bash(command, result="", cwd="/target"):
    return ("Bash", {"command": command}, result, cwd)


def tool(name, **tool_input):
    return (name, tool_input, "", "/target")


@pytest.fixture
def measure(tmp_path):
    def measure(*calls, source_language="python"):
        (tmp_path / "manifest.json").write_text(json.dumps({"condition": {"source_language": source_language}}))
        session = tmp_path / "transcript" / ".claude" / "projects" / "-target" / "s.jsonl"
        session.parent.mkdir(parents=True, exist_ok=True)
        records = []
        for i, (name, tool_input, result, cwd) in enumerate(calls):
            time = f"2026-01-01T00:{i // 60:02d}:{i % 60:02d}Z"
            block = {"type": "tool_use", "id": f"u{i}", "name": name, "input": tool_input}
            records.append({"type": "assistant", "timestamp": time, "cwd": cwd, "message": {"id": f"m{i}", "content": [block], "usage": USAGE}})
            records.append({"type": "user", "timestamp": time, "message": {"content": [{"type": "tool_result", "tool_use_id": f"u{i}", "content": result}]}})
        session.write_text("".join(json.dumps(r) + "\n" for r in records))
        return measure_transcript(tmp_path)

    return measure


def describe_tool_calls():
    def it_counts_turns_and_calls_by_tool(measure):
        result = measure(
            bash("ls"), bash("pwd"), tool("Read", file_path="/a"), tool("Write", file_path="/tmp/a", content=""),
            tool("Edit", file_path="/tmp/a"), tool("Glob", pattern="*"), tool("Grep", pattern="x"), tool("TodoWrite"),
        )
        assert {k: result[k] for k in ("turns", "bash_calls", "read_calls", "write_calls", "edit_calls", "search_calls")} == {
            "turns": 8, "bash_calls": 2, "read_calls": 1, "write_calls": 1, "edit_calls": 1, "search_calls": 2,
        }


def describe_reads():
    def it_counts_read_calls_and_reading_commands_by_class(measure):
        result = measure(
            tool("Read", file_path="/input/python/gbnf/graph.py"),
            tool("Read", file_path="/input/python/gbnf/graph_test.py"),
            bash("cd /input/python/gbnf && cat graph.py rules.py && head -5 graph_test.py"),
            bash("sed -n 1,20p /input/javascript/integration-tests/generated/a.test.ts"),
            bash("grep -n gbnf /input/python/tests/generated/x_test.py; less /input/python/gbnf/a.py"),
            bash("ls /input/python/gbnf; wc -l /input/python/gbnf/graph.py"),
        )
        assert (result["read_source"], result["read_source_tests"], result["read_target_tests"]) == (3, 3, 1)

    def it_skips_the_pattern_or_script_argument(measure):
        result = measure(bash("grep -rn /input/python/gbnf/x.py /tmp; sed -n /input/python/gbnf/x.py /tmp/y"))
        assert result["read_source"] == 0

    def it_marks_tests_touched_by_any_command(measure):
        result = measure(bash("ls /input/javascript/integration-tests/generated"))
        assert (result["touched_source_tests"], result["touched_target_tests"]) == (False, True)
        assert result["read_target_tests"] == 0


def describe_suite_runs():
    def it_records_each_run_with_its_turn_class_and_counts(measure):
        result = measure(
            bash("cp -r /input/javascript/integration-tests/generated /target/tests/"),
            bash("cd /target && pytest -q tests 2>&1 | tail -3", result="770 passed, 3 failed in 1.0s"),
            bash("cd /input/python && uv run --offline pytest -q", result="5 passed in 0.1s"),
        )
        assert result["suite_runs"] == [
            {"turn": 2, "command": "pytest -q tests", "suite": "target_tests", "passed": 770, "failed": 3},
            {"turn": 3, "command": "uv run --offline pytest -q", "suite": "source_tests", "passed": 5, "failed": 0},
        ]
        assert result["suite_run_count"] == 2
        assert result["last_suite_run_turn"] == 3
        assert result["touched_target_tests"] is True

    def it_pairs_several_runs_in_one_command_with_their_summaries_in_order(measure):
        result = measure(bash(
            "vitest run src/a.test.ts | tail -3; vitest run src/b.test.ts | tail -3",
            result="      Tests  1 passed (1)\n      Tests  1 failed | 2 passed (3)",
        ))
        assert [(r["passed"], r["failed"]) for r in result["suite_runs"]] == [(1, 0), (2, 1)]

    def it_leaves_counts_null_when_summaries_and_runs_do_not_pair(measure):
        result = measure(bash("pytest -q a_test.py; pytest -q b_test.py", result="1 passed in 0.1s"))
        assert [(r["passed"], r["failed"]) for r in result["suite_runs"]] == [(None, None), (None, None)]

    def it_classes_the_agents_own_tests(measure):
        result = measure(
            bash("cat > src/a.test.ts <<'EOF'\ntest('x', () => {})\nEOF"),
            bash("vitest run src/a.test.ts", result="Tests  1 passed (1)"),
        )
        assert result["suite_runs"][0]["suite"] == "own_tests"

    def it_keeps_the_last_counts_seen_per_class(measure):
        result = measure(
            bash("pytest /input/python/tests", result="1 failed, 1 passed in 0.1s"),
            bash("pytest /input/python/tests", result="2 passed in 0.1s"),
            bash("pytest /input/python/tests", result="Killed"),
        )
        assert result["last_suite_counts"] == {"source_tests": {"passed": 2, "failed": 0}}


def describe_own_tests():
    def it_lists_test_files_written_under_the_port(measure):
        result = measure(
            tool("Write", file_path="/target/gbnf/graph_test.py", content=""),
            bash("cd /target/gbnf && cat > rules_test.py <<'EOF'\nx\nEOF\ncat > rules.py <<'EOF'\ny\nEOF"),
            tool("Write", file_path="/target/gbnf/graph_test.py", content=""),
            tool("Write", file_path="/tmp/scratch_test.py", content=""),
        )
        assert result["own_test_files"] == ["/target/gbnf/graph_test.py", "/target/gbnf/rules_test.py"]
        assert result["own_tests_written"] == 2

    def it_counts_a_test_copied_in_from_scratch(measure):
        result = measure(bash("cp /tmp/smoke.test.ts /target/src/"))
        assert result["own_test_files"] == ["/target/src/smoke.test.ts"]

    def it_keeps_an_edited_copy_of_a_shipped_test_shipped(measure):
        result = measure(bash("cp -r /input/javascript/integration-tests /target/"), tool("Edit", file_path="/target/integration-tests/a.test.ts"), bash("vitest run integration-tests"))
        assert result["own_test_files"] == []
        assert result["suite_runs"][0]["suite"] == "target_tests"

    def it_does_not_count_a_copied_suite(measure):
        result = measure(bash("cp -r /input/python/tests /target/"), source_language="javascript")
        assert result["own_test_files"] == []


def describe_differential_script():
    def it_finds_a_command_that_runs_both_runtimes(measure):
        result = measure(bash("python3 --version; node --version"), bash("cd /tmp/d && python3 run.py && node run.mjs"))
        assert result["differential_script"] is True
        assert result["differential_evidence"] == {"turn": 2, "command": "cd /tmp/d && python3 run.py && node run.mjs"}

    def it_finds_a_heredoc_script_that_calls_the_other_runtime(measure):
        command = "python3 - <<'EOF'\nimport subprocess\nsubprocess.run(['node', 'x.mjs'])\nEOF"
        assert measure(bash(command))["differential_evidence"] == {"turn": 1, "command": command}

    def it_finds_a_written_file_that_calls_both_runtimes(measure):
        result = measure(tool("Write", file_path="/tmp/diff.sh", content="python3 a.py > a.json\nnode b.mjs > b.json\n"))
        assert result["differential_evidence"] == {"turn": 1, "path": "/tmp/diff.sh"}

    def it_finds_a_script_that_names_both_implementations(measure):
        content = "import GBNF from '/target/src/index.ts';\nconst ref = read('/input/python/gbnf/__init__.py');\n"
        result = measure(tool("Write", file_path="/tmp/cmp.mjs", content=content))
        assert result["differential_evidence"] == {"turn": 1, "path": "/tmp/cmp.mjs"}

    def it_is_false_otherwise(measure):
        result = measure(bash("node --version; python3 -c 'print(1)'"), bash("pytest && vitest run"))
        assert (result["differential_script"], result["differential_evidence"]) == (False, None)


def describe_fetch_attempts():
    def it_lists_web_tools_and_network_commands(measure):
        result = measure(
            tool("WebFetch", url="https://x.org"),
            tool("WebSearch", query="gbnf"),
            bash("curl -s https://x.org | head; pip install pytest-describe"),
            bash("npm install vitest; uv pip install x; npm test"),
        )
        assert result["fetch_commands"] == [
            {"turn": 1, "command": "WebFetch https://x.org"},
            {"turn": 2, "command": "WebSearch gbnf"},
            {"turn": 3, "command": "curl -s https://x.org"},
            {"turn": 3, "command": "pip install pytest-describe"},
            {"turn": 4, "command": "npm install vitest"},
            {"turn": 4, "command": "uv pip install x"},
        ]
        assert result["fetch_attempts"] == 6


def describe_tokens():
    def it_sums_usage_by_kind(measure):
        result = measure(bash("ls"), bash("ls"))
        assert {k: result[k] for k in ("input_tokens", "output_tokens", "cache_read_tokens", "cache_creation_tokens")} == {
            "input_tokens": 2, "output_tokens": 20, "cache_read_tokens": 200, "cache_creation_tokens": 2000,
        }

    def it_splits_the_total_at_the_first_write_into_the_port(measure):
        result = measure(bash("ls"), bash("echo x > /tmp/a"), bash("cat > gbnf/a.py <<'EOF'\nx\nEOF"), bash("ls"))
        assert (result["first_write_turn"], result["tokens_before_first_write"], result["tokens_after_first_write"]) == (3, 2222, 2222)

    def it_splits_at_a_write_or_edit_call(measure):
        result = measure(bash("ls"), tool("Edit", file_path="/target/a.py"))
        assert (result["first_write_turn"], result["tokens_before_first_write"]) == (2, 1111)

    def it_counts_a_write_into_a_copy_of_the_reference(measure):
        result = measure(bash("cp -r /input/python/. /target/"), bash("cat > /target/gbnf/a.py <<'EOF'\nx\nEOF"), tool("Read", file_path="/target/gbnf/a.py"))
        assert result["first_write_turn"] == 2
        assert result["read_source"] == 0

    def it_leaves_the_split_null_without_a_write(measure):
        result = measure(bash("ls"))
        assert (result["first_write_turn"], result["tokens_before_first_write"], result["tokens_after_first_write"]) == (None, None, None)
        assert result["last_suite_run_turn"] is None


def describe_manifest():
    def it_rejects_an_unknown_source_language(measure):
        with pytest.raises(ValueError, match="source_language"):
            measure(bash("ls"), source_language="typescript")
