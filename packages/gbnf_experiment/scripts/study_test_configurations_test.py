import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from itertools import islice
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from study_test_configurations import (
    MODELS,
    cell_key,
    cell_name,
    cells,
    main,
    schedule,
    study_test_configurations,
)

API_KEY = "sk-ant-test"
NAMES = (
    f"source-python_effort-low_model-{MODELS[0]}",
    f"source-python_effort-xhigh_model-{MODELS[0]}",
)


@pytest.fixture
def run_directory(tmp_path):
    directory = tmp_path / "runs" / "20261012T000000Z_00000000"
    directory.mkdir(parents=True)
    (directory / "manifest.json").write_text(json.dumps({"exit_code": 0}))
    (directory / "result.json").write_text(json.dumps({"usage": {"output_tokens": 7}}))
    return directory


CREDIT = {"is_error": True, "terminal_reason": "api_error", "result": "Credit balance is too low"}


def failed_run(tmp_path: Path, name: str, result: dict | None = None, stderr: str = "") -> Path:
    directory = tmp_path / "runs" / name
    directory.mkdir(parents=True)
    (directory / "manifest.json").write_text(json.dumps({"exit_code": 1}))
    if result is not None:
        (directory / "result.json").write_text(json.dumps(result))
    (directory / "stderr.txt").write_text(stderr)
    return directory


def write_jsonl(path: Path, records: list[tuple[dict, int]]) -> Path:
    path.write_text("".join(json.dumps({"cell": cell, "exit_code": code}) + "\n" for cell, code in records))
    return path


@pytest.fixture
def gbnf_experiment(run_directory):
    with patch("study_test_configurations.run_gbnf_experiment", autospec=True) as m:
        m.return_value = run_directory
        yield m


@pytest.fixture(autouse=True)
def claude_agent():
    with patch("study_test_configurations.ClaudeAgent", autospec=True) as m:
        yield m


@pytest.fixture(autouse=True)
def prepare():
    with patch("study_test_configurations.prepare_reference_implementation", autospec=True) as m:
        yield m


@pytest.fixture(autouse=True)
def threads():
    # Mocks do not cross a process boundary, and only the main thread may set a signal handler.
    with patch("study_test_configurations.ProcessPoolExecutor", lambda parallel, **_: ThreadPoolExecutor(parallel)):
        yield


def read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def describe_cells():
    def it_is_directions_by_test_flags_by_models():
        assert len(cells()) == 2 * 8 * 4
        assert len({cell_name(cell) for cell in cells()}) == 64

    def it_covers_every_model():
        assert {cell["model"] for cell in cells()} == set(MODELS)

    def it_runs_at_medium_effort_by_default():
        assert {cell["effort"] for cell in cells()} == {"medium"}

    def it_multiplies_the_cells_by_each_effort():
        both = cells(efforts=("low", "xhigh"))
        assert len(both) == 128
        assert len({cell_name(cell) for cell in both}) == 128


def describe_schedule():
    def it_runs_every_cell_once_per_round():
        everything = cells()
        runs = list(schedule(everything, n=3))
        for r in (1, 2, 3):
            this_round = [cell_name(cell) for rr, cell in runs if rr == r]
            assert sorted(this_round) == sorted(cell_name(cell) for cell in everything)

    def it_finishes_a_round_before_starting_the_next():
        rounds = [r for r, _ in schedule(cells(), n=3)]
        assert rounds == sorted(rounds)

    def it_shuffles_each_round_afresh():
        runs = list(schedule(cells(), n=2))
        first, second = runs[:64], runs[64:]
        assert [cell_name(c) for _, c in first] != [cell_name(c) for _, c in second]

    def it_is_unbounded_without_n():
        assert len(list(islice(schedule(cells(), n=None), 64 * 5))) == 64 * 5

    def it_never_lets_one_cell_get_two_runs_ahead_of_another():
        everything = cells()
        counts = Counter({cell_name(cell): 0 for cell in everything})
        for _, cell in schedule(everything, n=4):
            counts[cell_name(cell)] += 1
            assert max(counts.values()) - min(counts.values()) <= 1


def describe_run_matrix():
    def it_writes_one_line_per_run(tmp_path, gbnf_experiment):
        out = tmp_path / "matrix.jsonl"
        study_test_configurations(cells(), n=2, parallel=2, api_key=API_KEY, out=out)
        assert len(read(out)) == 128

    def it_writes_the_cell_round_run_directory_exit_code_wall_time_and_usage(
        tmp_path, gbnf_experiment, run_directory
    ):
        out = tmp_path / "matrix.jsonl"
        [cell] = cells(efforts=("high",))[:1]
        study_test_configurations([cell], n=1, parallel=1, api_key=API_KEY, out=out)
        [line] = read(out)
        assert line["cell"] == cell
        assert line["cell"]["effort"] == "high"
        assert line["round"] == 1
        assert line["run_directory"] == str(run_directory)
        assert line["error"] is None
        assert line["exit_code"] == 0
        assert line["wall_seconds"] >= 0
        assert line["usage"] == {"output_tokens": 7}

    def it_keeps_going_when_a_run_raises(tmp_path, gbnf_experiment, run_directory):
        gbnf_experiment.side_effect = [RuntimeError("boom"), *[run_directory] * 63]
        out = tmp_path / "matrix.jsonl"
        study_test_configurations(cells(), n=1, parallel=1, api_key=API_KEY, out=out)
        lines = read(out)
        assert len(lines) == 64
        assert lines[0]["error"] == "boom"
        assert lines[0]["run_directory"] is None
        assert all(line["error"] is None for line in lines[1:])

    def it_logs_runs_so_that_any_prefix_is_balanced_across_cells(tmp_path, gbnf_experiment):
        out = tmp_path / "matrix.jsonl"
        everything = cells()
        study_test_configurations(everything, n=3, parallel=1, api_key=API_KEY, out=out)
        counts = Counter({cell_name(cell): 0 for cell in everything})
        for line in read(out):
            counts[cell_name(line["cell"])] += 1
            assert max(counts.values()) - min(counts.values()) <= 1

    def it_writes_runs_in_round_order(tmp_path, gbnf_experiment):
        out = tmp_path / "matrix.jsonl"
        study_test_configurations(cells(), n=2, parallel=1, api_key=API_KEY, out=out)
        rounds = [line["round"] for line in read(out)]
        assert rounds == [1] * 64 + [2] * 64

    def it_gives_each_agent_the_key_and_its_cell_s_model_and_effort(
        tmp_path, gbnf_experiment, claude_agent
    ):
        two = [cell for cell in cells(efforts=("low", "xhigh")) if cell_name(cell) in NAMES]
        study_test_configurations(two, n=1, parallel=1, api_key=API_KEY, out=tmp_path / "m")
        assert sorted(c.kwargs["effort"] for c in claude_agent.call_args_list) == ["low", "xhigh"]
        for c in claude_agent.call_args_list:
            assert c.kwargs == {"model": MODELS[0], "effort": c.kwargs["effort"], "api_key": API_KEY}

    def it_warms_every_condition_before_the_first_run(tmp_path, gbnf_experiment, prepare):
        order = Mock()
        order.attach_mock(prepare, "prepare")
        order.attach_mock(gbnf_experiment, "run")
        study_test_configurations(cells(), n=1, parallel=2, api_key=API_KEY, out=tmp_path / "m")
        names = [name for name, _, _ in order.mock_calls]
        assert names[:16] == ["prepare"] * 16
        assert "prepare" not in names[16:]


@pytest.fixture
def matrix(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", API_KEY)
    with patch("study_test_configurations.study_test_configurations", autospec=True) as m:
        m.return_value = None
        yield m


def describe_main():
    @pytest.mark.parametrize("environment", [{}, {"ANTHROPIC_API_KEY": ""}])
    def it_refuses_to_start_without_an_api_key(
        environment, monkeypatch, capsys, gbnf_experiment, prepare, claude_agent
    ):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        for key, value in environment.items():
            monkeypatch.setenv(key, value)
        with pytest.raises(SystemExit) as exit:
            main(["--n", "1"])
        assert exit.value.code != 0
        assert "ANTHROPIC_API_KEY" in str(exit.value.code)
        prepare.assert_not_called()
        gbnf_experiment.assert_not_called()
        claude_agent.assert_not_called()

    def it_runs_twelve_rounds_of_opus_at_medium_effort_by_default(matrix):
        main([])
        selected = matrix.call_args.args[0]
        assert len(selected) == 16
        assert {(cell["model"], cell["effort"]) for cell in selected} == {
            ("claude-opus-5-5", "medium")
        }
        assert matrix.call_args.kwargs["n"] == 12

    def it_runs_four_jobs_at_once_by_default(matrix):
        main([])
        assert matrix.call_args.kwargs["parallel"] == 4

    @pytest.mark.parametrize("flag", ["-k", "--parallel"])
    def it_takes_k_as_the_number_of_concurrent_jobs(flag, matrix):
        main([flag, "6"])
        assert matrix.call_args.kwargs["parallel"] == 6

    def it_runs_until_stopped_at_n_zero(matrix):
        main(["--n", "0"])
        assert matrix.call_args.kwargs["n"] is None

    def it_runs_every_cell_at_every_effort_and_model_given(matrix):
        main(["--efforts", "low,xhigh", "--models", *MODELS])
        selected = matrix.call_args.args[0]
        assert len(selected) == 128
        assert {cell["effort"] for cell in selected} == {"low", "xhigh"}

    def it_selects_cells_by_name_including_effort(matrix):
        main(["--efforts", "low,xhigh", "--cells", NAMES[1]])
        [cell] = matrix.call_args.args[0]
        assert cell["effort"] == "xhigh"


def describe_resume():
    def it_runs_each_cell_up_to_n_counting_prior_successes():
        everything = cells()[:3]
        prior = Counter({cell_key(everything[0]): 3, cell_key(everything[1]): 5})
        runs = Counter(cell_name(cell) for _, cell in schedule(everything, n=5, prior=prior))
        assert runs == {cell_name(everything[0]): 2, cell_name(everything[2]): 5}

    def it_drops_a_cell_out_of_the_round_robin_once_it_reaches_its_target():
        everything = cells()[:3]
        prior = Counter({cell_key(everything[0]): 3})
        runs = list(schedule(everything, n=5, prior=prior))
        assert [r for r, _ in runs] == [1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5]

    def it_counts_exit_code_zero_per_full_cell_across_every_file(tmp_path, matrix):
        opus, sonnet = (
            next(cell for cell in cells() if cell["model"] == model) for model in ("claude-opus-5-5", "claude-sonnet-5-5")
        )
        first = write_jsonl(tmp_path / "a.jsonl", [(opus, 0), (opus, 1), (opus, 137), (sonnet, 0)])
        second = write_jsonl(tmp_path / "b.jsonl", [(opus, 0), (opus, None)])
        main(["--resume", str(first), str(second)])
        assert matrix.call_args.kwargs["prior"] == {cell_key(opus): 2, cell_key(sonnet): 1}

    def it_prints_each_cell_s_shortfall_and_the_total(tmp_path, matrix, capsys):
        [opus] = [cell for cell in cells() if cell["model"] == "claude-opus-5-5"][:1]
        path = write_jsonl(tmp_path / "a.jsonl", [(opus, 0)] * 5)
        main(["--resume", str(path)])
        err = capsys.readouterr().err
        assert f"{cell_name(opus)}=7" in err
        assert "total 187" in err


def describe_runs():
    def it_stops_submitting_after_n_runs_in_round_robin_order(tmp_path, gbnf_experiment):
        out = tmp_path / "matrix.jsonl"
        study_test_configurations(cells(), n=2, parallel=2, api_key=API_KEY, out=out, runs=5)
        lines = read(out)
        assert len(lines) == 5
        assert {line["round"] for line in lines} == {1}

    def it_passes_runs_from_the_command_line(matrix):
        main(["--runs", "4"])
        assert matrix.call_args.kwargs["runs"] == 4

    def it_is_unlimited_by_default(matrix):
        main([])
        assert matrix.call_args.kwargs["runs"] is None


def describe_record():
    def it_writes_utc_start_and_finish_times(tmp_path, gbnf_experiment):
        out = tmp_path / "matrix.jsonl"
        study_test_configurations(cells()[:1], n=1, parallel=1, api_key=API_KEY, out=out)
        [line] = read(out)
        started, finished = (datetime.fromisoformat(line[key]) for key in ("started_at", "finished_at"))
        assert started.utcoffset().total_seconds() == 0
        assert started <= finished

    def it_writes_the_terminal_reason_and_the_first_300_characters_of_the_result(tmp_path, gbnf_experiment):
        gbnf_experiment.return_value = failed_run(
            tmp_path, "long", {"is_error": False, "terminal_reason": "completed", "result": "x" * 1000}
        )
        out = tmp_path / "matrix.jsonl"
        study_test_configurations(cells()[:1], n=1, parallel=1, api_key=API_KEY, out=out)
        [line] = read(out)
        assert line["terminal_reason"] == "completed"
        assert line["result"] == "x" * 300

    def it_writes_none_without_a_result_json(tmp_path, gbnf_experiment):
        gbnf_experiment.return_value = failed_run(tmp_path, "none")
        out = tmp_path / "matrix.jsonl"
        study_test_configurations(cells()[:1], n=1, parallel=1, api_key=API_KEY, out=out)
        [line] = read(out)
        assert (line["terminal_reason"], line["result"], line["usage"]) == (None, None, None)


def describe_fail_fast():
    @pytest.mark.parametrize(
        ("result", "stderr"),
        [
            (CREDIT, ""),
            ({"is_error": True, "terminal_reason": "completed", "result": "OAuth token has expired"}, ""),
            ({"is_error": True, "terminal_reason": "completed", "result": "API Error: 401"}, ""),
            (None, "Not logged in · Please run /login"),
            (None, "Invalid authentication credentials"),
        ],
    )
    def it_stops_at_the_first_credit_or_auth_failure(tmp_path, gbnf_experiment, capsys, result, stderr):
        exhausted = failed_run(tmp_path, "exhausted", result, stderr)
        gbnf_experiment.return_value = exhausted
        out = tmp_path / "matrix.jsonl"
        stopped = study_test_configurations(cells(), n=2, parallel=1, api_key=API_KEY, out=out)
        [line] = read(out)
        assert stopped == line
        assert f"STOPPED: round 1 {cell_name(line['cell'])} {exhausted}: " in capsys.readouterr().err

    def it_lets_the_in_flight_runs_finish_and_names_the_first(tmp_path, gbnf_experiment, capsys):
        gbnf_experiment.return_value = failed_run(tmp_path, "exhausted", CREDIT)
        out = tmp_path / "matrix.jsonl"
        stopped = study_test_configurations(cells(), n=2, parallel=4, api_key=API_KEY, out=out)
        lines = read(out)
        assert len(lines) == 4
        assert stopped == lines[0]
        err = capsys.readouterr().err.splitlines()
        [stop] = [index for index, text in enumerate(err) if text.startswith("STOPPED:")]
        assert err[stop].endswith(": Credit balance is too low")
        assert len(err) == stop + 2

    def it_keeps_going_on_other_failures(tmp_path, gbnf_experiment):
        gbnf_experiment.return_value = failed_run(
            tmp_path, "other", {"is_error": True, "terminal_reason": "max_turns", "result": "too many turns"}
        )
        out = tmp_path / "matrix.jsonl"
        assert study_test_configurations(cells(), n=1, parallel=2, api_key=API_KEY, out=out) is None
        assert len(read(out)) == 64

    def it_exits_non_zero_when_stopped(matrix):
        matrix.return_value = {"round": 1}
        with pytest.raises(SystemExit) as exit:
            main([])
        assert exit.value.code != 0


def describe_auth():
    def it_gives_each_agent_no_key_on_subscription(tmp_path, gbnf_experiment, claude_agent):
        study_test_configurations(cells()[:1], n=1, parallel=1, api_key=None, out=tmp_path / "m")
        assert claude_agent.call_args.kwargs["api_key"] is None

    def it_passes_no_key_on_subscription(monkeypatch, matrix):
        monkeypatch.delenv("ANTHROPIC_API_KEY")
        main(["--auth", "subscription"])
        assert matrix.call_args.kwargs["api_key"] is None

    def it_refuses_subscription_while_an_api_key_is_set(matrix):
        with pytest.raises(SystemExit) as exit:
            main(["--auth", "subscription"])
        assert "ANTHROPIC_API_KEY" in str(exit.value.code)
        matrix.assert_not_called()

    @pytest.mark.parametrize("auth", ["api-key", "subscription"])
    def it_names_the_auth_mode_at_startup(auth, monkeypatch, matrix, capsys):
        if auth == "subscription":
            monkeypatch.delenv("ANTHROPIC_API_KEY")
        main(["--auth", auth])
        assert f"auth {auth}" in capsys.readouterr().err
