import json

STEPS = [
    {"type": "user", "message": {"role": "user", "content": "Port the implementation under python/ to typescript."}},
    {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Looking at the source first."}]}},
    {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "ls /input"}}]}},
    {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "SECRET-TOOL-OUTPUT"}]}},
    {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": "t2", "name": "Write", "input": {"file_path": "/target/src/index.ts", "content": "x" * 2500}}]}},
]


def describe_judge_run():
    def describe_code():
        def it_judges_the_human_pair_both_ways_and_each_run_once(run_cli, make_run, calls, read_out, tmp_path):
            make_run("20261012T000000Z_aaaaaaaa", "python")
            make_run("20261012T000000Z_bbbbbbbb", "javascript", flags=(True, False, False))
            result = run_cli("run", "--rubric", "code", "--runs", tmp_path / "runs", "--out", tmp_path / "out")
            assert result.returncode == 0, result.stderr
            judgments, manifest = read_out(tmp_path / "out")
            assert len(calls()) == len(judgments) == len(manifest) == 4
            assert sorted(((e["run"], e["baseline"], e["source_language"]) for e in manifest.values()), key=str) == sorted([
                (None, True, "python"),
                (None, True, "javascript"),
                ("20261012T000000Z_aaaaaaaa", False, "python"),
                ("20261012T000000Z_bbbbbbbb", False, "javascript"),
            ], key=str)
            assert {j["id"] for j in judgments} == set(manifest)
            assert all(j["verdicts"]["fidelity"]["verdict"] == 4 for j in judgments)

        def it_compares_the_pinned_human_implementations_with_tests_left_out(run_cli, calls, tmp_path):
            (tmp_path / "runs").mkdir()
            run_cli("run", "--rubric", "code", "--runs", tmp_path / "runs", "--out", tmp_path / "out")
            prompts = [call["prompt"] for call in calls()]
            assert len(prompts) == 2
            forward = next(p for p in prompts if "=== A: gbnf/GBNF.py ===" in p)
            reverse = next(p for p in prompts if "=== B: gbnf/GBNF.py ===" in p)
            assert "=== B: src/gbnf.ts ===" in forward and "=== A: src/gbnf.ts ===" in reverse
            assert all("_test.py ===" not in p and ".test.ts ===" not in p and ": src/builder/" not in p for p in prompts)

        def it_shows_the_judge_the_rubric_verbatim_and_nothing_that_identifies_the_item(run_cli, make_run, calls, rubric, tmp_path):
            make_run("20261012T000000Z_aaaaaaaa", "python")
            run_cli("run", "--rubric", "code", "--runs", tmp_path / "runs", "--out", tmp_path / "out")
            assert len(calls()) == 3
            for call in calls():
                assert call["prompt"].startswith(rubric("code"))
                for marker in ("aaaaaaaa", "ported_implementation", "baseline", "human", "agent", str(tmp_path)):
                    assert marker not in call["prompt"]

    def describe_transcript():
        def it_judges_each_run_on_its_compressed_transcript_alone(run_cli, make_run, calls, read_out, rubric, tmp_path):
            make_run("20261012T000000Z_aaaaaaaa", "python", steps=STEPS)
            result = run_cli("run", "--rubric", "transcript", "--runs", tmp_path / "runs", "--out", tmp_path / "out")
            assert result.returncode == 0, result.stderr
            [call] = calls()
            item = call["prompt"].removeprefix(rubric("transcript"))
            assert "[1] text: Looking at the source first.\n" in item
            assert '[2] Bash: {"command": "ls /input"}\n' in item
            assert "[500 more characters cut]" in item
            assert "SECRET-TOOL-OUTPUT" not in item and "Port the implementation" not in item
            judgments, manifest = read_out(tmp_path / "out")
            assert [e["run"] for e in manifest.values()] == ["20261012T000000Z_aaaaaaaa"]

        def it_asks_for_a_reading_strategy_from_its_fixed_set_with_quoted_steps(run_cli, make_run, calls, tmp_path):
            make_run("20261012T000000Z_aaaaaaaa", "python", steps=STEPS)
            run_cli("run", "--rubric", "transcript", "--runs", tmp_path / "runs", "--out", tmp_path / "out")
            [call] = calls()
            schema = json.loads(call["argv"][call["argv"].index("--json-schema") + 1])
            assert "reading_strategy" in schema["required"]
            item = schema["properties"]["reading_strategy"]
            assert item["properties"]["verdict"]["enum"] == ["entry-point-traced", "directory-order", "tests-first", "mixed", "unclear"]
            assert set(item["required"]) == {"verdict", "evidence", "confidence"}

    def it_calls_claude_on_the_subscription_with_tools_off_from_an_empty_directory(run_cli, make_run, calls, tmp_path):
        make_run("20261012T000000Z_aaaaaaaa", "python", steps=STEPS)
        run_cli("run", "--rubric", "transcript", "--runs", tmp_path / "runs", "--out", tmp_path / "out", "--model", "claude-test", "--effort", "low")
        [call] = calls()
        assert call["api_key"] is False
        argv = call["argv"]
        assert argv[argv.index("--tools") + 1] == ""
        assert (argv[argv.index("--model") + 1], argv[argv.index("--effort") + 1]) == ("claude-test", "low")
        assert not str(call["cwd"]).startswith(str(tmp_path))

    def it_records_id_rubric_model_verdicts_raw_text_usage_and_wall_seconds(run_cli, make_run, read_out, tmp_path):
        make_run("20261012T000000Z_aaaaaaaa", "python", steps=STEPS)
        run_cli("run", "--rubric", "transcript", "--runs", tmp_path / "runs", "--out", tmp_path / "out")
        [judgment], manifest = read_out(tmp_path / "out")
        assert set(judgment) == {"id", "rubric", "model", "effort", "verdicts", "raw", "usage", "wall_seconds"}
        assert (judgment["rubric"], judgment["model"], judgment["effort"]) == ("transcript", "claude-opus-5-5", "max")
        assert json.loads(judgment["raw"]) == judgment["verdicts"]
        assert judgment["usage"]["output_tokens"] == 100
        entry = manifest[judgment["id"]]
        assert entry["tokens_estimate"] == entry["prompt_chars"] // 4

    def it_skips_items_already_judged_when_run_again(run_cli, make_run, calls, read_out, tmp_path):
        make_run("20261012T000000Z_aaaaaaaa", "python", steps=STEPS)
        make_run("20261012T000000Z_bbbbbbbb", "javascript", steps=STEPS[:2])
        args = ("run", "--rubric", "transcript", "--runs", tmp_path / "runs", "--out", tmp_path / "out")
        run_cli(*args, "--limit", 1)
        assert len(calls()) == 1
        run_cli(*args)
        assert len(calls()) == 2
        run_cli(*args)
        assert len(calls()) == 2
        judgments, _ = read_out(tmp_path / "out")
        assert len({j["id"] for j in judgments}) == len(judgments) == 2

    def describe_replicate_fraction():
        def it_writes_no_replicates_by_default(run_cli, make_run, tmp_path):
            make_run("20261012T000000Z_aaaaaaaa", "python")
            run_cli("run", "--rubric", "code", "--runs", tmp_path / "runs", "--out", tmp_path / "out")
            assert sorted(p.name for p in (tmp_path / "out").iterdir()) == ["judgments.jsonl", "manifest.json"]

        def it_judges_the_baselines_a_second_time_with_the_same_prompt(run_cli, make_run, calls, read_out, tmp_path):
            make_run("20261012T000000Z_aaaaaaaa", "python")
            args = ("run", "--rubric", "code", "--runs", tmp_path / "runs", "--out", tmp_path / "out", "--replicate-fraction", 1e-9)
            result = run_cli(*args)
            assert result.returncode == 0, result.stderr
            judgments, manifest = read_out(tmp_path / "out")
            replicates = [json.loads(line) for line in (tmp_path / "out" / "replicates.jsonl").read_text().splitlines()]
            assert len(judgments) == 3
            assert sorted(r["id"] for r in replicates) == sorted(i for i, e in manifest.items() if e["baseline"])
            assert set(replicates[0]) == set(judgments[0])
            prompts = [call["prompt"] for call in calls()]
            assert len(prompts) == 5
            assert sorted(prompts.count(p) for p in set(prompts)) == [1, 2, 2]
            run_cli(*args)
            assert len(calls()) == 5

        def it_replicates_every_item_at_one(run_cli, make_run, read_out, tmp_path):
            make_run("20261012T000000Z_aaaaaaaa", "python", steps=STEPS)
            make_run("20261012T000000Z_bbbbbbbb", "javascript", steps=STEPS[:2])
            run_cli("run", "--rubric", "transcript", "--runs", tmp_path / "runs", "--out", tmp_path / "out", "--replicate-fraction", 1)
            judgments, _ = read_out(tmp_path / "out")
            replicates = [json.loads(line) for line in (tmp_path / "out" / "replicates.jsonl").read_text().splitlines()]
            assert sorted(r["id"] for r in replicates) == sorted(j["id"] for j in judgments)

    def it_leaves_out_runs_whose_agent_did_not_exit_0(run_cli, make_run, read_out, tmp_path):
        make_run("20261012T000000Z_aaaaaaaa", "python", steps=STEPS)
        make_run("20261012T000000Z_cccccccc", "python", steps=STEPS, exit_code=137)
        run_cli("run", "--rubric", "transcript", "--runs", tmp_path / "runs", "--out", tmp_path / "out")
        _, manifest = read_out(tmp_path / "out")
        assert [e["run"] for e in manifest.values()] == ["20261012T000000Z_aaaaaaaa"]

    def it_fails_and_writes_no_judgment_when_claude_fails(run_cli, make_run, tmp_path):
        make_run("20261012T000000Z_aaaaaaaa", "python", steps=STEPS)
        result = run_cli("run", "--rubric", "transcript", "--runs", tmp_path / "runs", "--out", tmp_path / "out", fail=True)
        assert result.returncode != 0
        assert "rate limited" in result.stderr
        assert not (tmp_path / "out" / "judgments.jsonl").exists() or (tmp_path / "out" / "judgments.jsonl").read_text() == ""


def describe_judge_report():
    def it_tables_verdicts_by_condition_prints_the_baselines_and_lists_unsure_items(run_cli, make_run, tmp_path):
        make_run("20261012T000000Z_aaaaaaaa", "python", flags=(False, True, True), steps=STEPS)
        run_cli("run", "--rubric", "code", "--runs", tmp_path / "runs", "--out", tmp_path / "out")
        run_cli("run", "--rubric", "transcript", "--runs", tmp_path / "runs", "--out", tmp_path / "out")
        result = run_cli("report", "--out", tmp_path / "out")
        assert result.returncode == 0, result.stderr
        lines = [line.split() for line in result.stdout.splitlines()]
        assert ["code", "fidelity"] in lines
        assert ["python", "unit=0", "source-int=1", "target-int=1", "1", "0", "0", "0", "1", "0"] in lines
        assert lines[lines.index(["transcript", "reading_strategy"]) + 2] == ["python", "unit=0", "source-int=1", "target-int=1", "1", "1", "0", "0", "0", "0"]
        baselines = [line for line in result.stdout.splitlines() if line.startswith("baseline ")]
        assert sorted(line.split()[1] for line in baselines) == ["javascript->python", "python->javascript"]
        assert all(line.endswith("fidelity=4") for line in baselines)
        unsure = result.stdout.split("unsure\n")[1].split()
        assert unsure[1:] == ["20261012T000000Z_aaaaaaaa", "transcript", "cheating:", "none"]
