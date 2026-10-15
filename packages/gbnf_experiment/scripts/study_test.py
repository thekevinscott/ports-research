import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from itertools import islice, product
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from study import FLAGS, SOURCE_LANGUAGES, argument_parser, cell_key, cell_name, main, run_study, schedule

API_KEY = "sk-ant-test"
STUDY = "v2-test-configurations"
MODELS = ("claude-opus-5-5", "claude-sonnet-5-5")


def cells(efforts=("medium",), models=MODELS) -> list[dict]:
    return [
        {"source_language": source_language, **dict(zip(FLAGS, flags)), "model": model, "effort": effort}
        for source_language, flags, model, effort in product(
            SOURCE_LANGUAGES, product((False, True), repeat=len(FLAGS)), models, efforts
        )
    ]


CELLS = cells()
NAMES = tuple(cell_name(cell) for cell in cells(efforts=("low", "xhigh"), models=MODELS[:1])[:2])


def parse(tmp_path: Path, argv: list[str]):
    return argument_parser("").parse_args(["--output", str(tmp_path / "runs"), *argv])


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


def banked_run(tmp_path: Path, name: str, cell: dict, study: str = STUDY, exit_code: int = 0, result: dict | None = None):
    directory = tmp_path / "runs" / name
    directory.mkdir(parents=True)
    manifest = {"study": study, "condition": cell, "exit_code": exit_code, "error": None, "completed_at": "2026-10-15"}
    (directory / "manifest.json").write_text(json.dumps(manifest))
    (directory / "result.json").write_text(json.dumps({"is_error": False} if result is None else result))


def bank(tmp_path: Path, runs: list[tuple[dict, int]], study: str = STUDY) -> None:
    for i, (cell, code) in enumerate(runs):
        banked_run(tmp_path, f"20261012T00000{i}Z_0000000{i}", cell, study, code)


@pytest.fixture
def gbnf_experiment(run_directory):
    with patch("study.run_gbnf_experiment", autospec=True) as m:
        m.return_value = run_directory
        yield m


@pytest.fixture(autouse=True)
def claude_agent():
    with patch("study.ClaudeAgent", autospec=True) as m:
        yield m


@pytest.fixture(autouse=True)
def prepare():
    with patch("study.prepare_reference_implementation", autospec=True) as m:
        yield m


@pytest.fixture(autouse=True)
def threads():
    # Mocks do not cross a process boundary, and only the main thread may set a signal handler.
    with patch("study.ProcessPoolExecutor", lambda parallel, **_: ThreadPoolExecutor(parallel)):
        yield


def read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def describe_schedule():
    def it_runs_every_cell_once_per_round():
        runs = list(schedule(CELLS, n=3))
        for r in (1, 2, 3):
            this_round = [cell_name(cell) for rr, cell in runs if rr == r]
            assert sorted(this_round) == sorted(cell_name(cell) for cell in CELLS)

    def it_finishes_a_round_before_starting_the_next():
        rounds = [r for r, _ in schedule(CELLS, n=3)]
        assert rounds == sorted(rounds)

    def it_shuffles_each_round_afresh():
        runs = list(schedule(CELLS, n=2))
        first, second = runs[:32], runs[32:]
        assert [cell_name(c) for _, c in first] != [cell_name(c) for _, c in second]

    def it_is_unbounded_without_n():
        assert len(list(islice(schedule(CELLS, n=None), 32 * 5))) == 32 * 5

    def it_never_lets_one_cell_get_two_runs_ahead_of_another():
        counts = Counter({cell_name(cell): 0 for cell in CELLS})
        for _, cell in schedule(CELLS, n=4):
            counts[cell_name(cell)] += 1
            assert max(counts.values()) - min(counts.values()) <= 1


def describe_run_study():
    def it_writes_one_line_per_run(tmp_path, gbnf_experiment):
        out = tmp_path / "matrix.jsonl"
        run_study(STUDY, CELLS, n=2, parallel=2, api_key=API_KEY, log=out, output=tmp_path / "runs")
        assert len(read(out)) == 64

    def it_writes_the_cell_round_run_directory_exit_code_wall_time_and_usage(
        tmp_path, gbnf_experiment, run_directory
    ):
        out = tmp_path / "matrix.jsonl"
        [cell] = cells(efforts=("high",))[:1]
        run_study(STUDY, [cell], n=1, parallel=1, api_key=API_KEY, log=out, output=tmp_path / "runs")
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
        gbnf_experiment.side_effect = [RuntimeError("boom"), *[run_directory] * 31]
        out = tmp_path / "matrix.jsonl"
        run_study(STUDY, CELLS, n=1, parallel=1, api_key=API_KEY, log=out, output=tmp_path / "runs")
        lines = read(out)
        assert len(lines) == 32
        assert lines[0]["error"] == "boom"
        assert lines[0]["run_directory"] is None
        assert all(line["error"] is None for line in lines[1:])

    def it_logs_runs_so_that_any_prefix_is_balanced_across_cells(tmp_path, gbnf_experiment):
        out = tmp_path / "matrix.jsonl"
        run_study(STUDY, CELLS, n=3, parallel=1, api_key=API_KEY, log=out, output=tmp_path / "runs")
        counts = Counter({cell_name(cell): 0 for cell in CELLS})
        for line in read(out):
            counts[cell_name(line["cell"])] += 1
            assert max(counts.values()) - min(counts.values()) <= 1

    def it_writes_runs_in_round_order(tmp_path, gbnf_experiment):
        out = tmp_path / "matrix.jsonl"
        run_study(STUDY, CELLS, n=2, parallel=1, api_key=API_KEY, log=out, output=tmp_path / "runs")
        rounds = [line["round"] for line in read(out)]
        assert rounds == [1] * 32 + [2] * 32

    def it_gives_each_agent_the_key_and_its_cell_s_model_and_effort(tmp_path, gbnf_experiment, claude_agent):
        two = [cell for cell in cells(efforts=("low", "xhigh")) if cell_name(cell) in NAMES]
        run_study(STUDY, two, n=1, parallel=1, api_key=API_KEY, log=tmp_path / "m", output=tmp_path / "runs")
        assert sorted(c.kwargs["effort"] for c in claude_agent.call_args_list) == ["low", "xhigh"]
        for c in claude_agent.call_args_list:
            assert c.kwargs == {"model": MODELS[0], "effort": c.kwargs["effort"], "api_key": API_KEY}

    def it_points_every_run_at_the_output_directory(tmp_path, gbnf_experiment):
        run_study(STUDY, CELLS[:3], n=1, parallel=1, api_key=API_KEY, log=tmp_path / "m", output=tmp_path / "runs")
        assert [c.kwargs["output"] for c in gbnf_experiment.call_args_list] == [tmp_path / "runs"] * 3

    def it_names_the_study_on_every_run(tmp_path, gbnf_experiment):
        run_study("v2-model-effort", CELLS[:3], n=1, parallel=1, api_key=API_KEY, log=tmp_path / "m", output=tmp_path / "runs")
        assert [c.kwargs["study"] for c in gbnf_experiment.call_args_list] == ["v2-model-effort"] * 3

    def it_warms_every_condition_before_the_first_run(tmp_path, gbnf_experiment, prepare):
        order = Mock()
        order.attach_mock(prepare, "prepare")
        order.attach_mock(gbnf_experiment, "run")
        run_study(STUDY, CELLS, n=1, parallel=2, api_key=API_KEY, log=tmp_path / "m", output=tmp_path / "runs")
        names = [name for name, _, _ in order.mock_calls]
        assert names[:16] == ["prepare"] * 16
        assert "prepare" not in names[16:]


@pytest.fixture
def study(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", API_KEY)
    with patch("study.run_study", autospec=True) as m:
        m.return_value = None
        yield m


def describe_main():
    @pytest.mark.parametrize("environment", [{}, {"ANTHROPIC_API_KEY": ""}])
    def it_refuses_to_start_without_an_api_key(
        environment, tmp_path, monkeypatch, capsys, gbnf_experiment, prepare, claude_agent
    ):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        for key, value in environment.items():
            monkeypatch.setenv(key, value)
        with pytest.raises(SystemExit) as exit:
            main(STUDY, CELLS, parse(tmp_path, ["--n", "1"]))
        assert exit.value.code != 0
        assert "ANTHROPIC_API_KEY" in str(exit.value.code)
        prepare.assert_not_called()
        gbnf_experiment.assert_not_called()
        claude_agent.assert_not_called()

    def it_runs_the_study_and_cells_it_is_given_for_twelve_rounds_by_default(tmp_path, study):
        main(STUDY, CELLS, parse(tmp_path, []))
        assert study.call_args.args == (STUDY, CELLS)
        assert study.call_args.kwargs["n"] == 12

    def it_requires_an_output_directory(capsys):
        """No default: a default landed runs in whichever checkout ran them."""
        with pytest.raises(SystemExit):
            argument_parser("").parse_args([])
        assert "--output" in capsys.readouterr().err

    def it_writes_the_jsonl_into_the_output_directory_and_runs_beside_it(tmp_path, study):
        main(STUDY, CELLS, parse(tmp_path, []))
        assert study.call_args.kwargs["output"] == tmp_path / "runs"
        assert study.call_args.kwargs["log"].parent == tmp_path / "runs"
        assert study.call_args.kwargs["log"].name.startswith("matrix-")

    def it_creates_the_output_directory(tmp_path, study):
        main(STUDY, CELLS, parse(tmp_path, []))
        assert (tmp_path / "runs").is_dir()

    def it_runs_four_jobs_at_once_by_default(tmp_path, study):
        main(STUDY, CELLS, parse(tmp_path, []))
        assert study.call_args.kwargs["parallel"] == 4

    @pytest.mark.parametrize("flag", ["-k", "--parallel"])
    def it_takes_k_as_the_number_of_concurrent_jobs(flag, tmp_path, study):
        main(STUDY, CELLS, parse(tmp_path, [flag, "6"]))
        assert study.call_args.kwargs["parallel"] == 6

    def it_runs_until_stopped_at_n_zero(tmp_path, study):
        main(STUDY, CELLS, parse(tmp_path, ["--n", "0"]))
        assert study.call_args.kwargs["n"] is None

    def it_names_the_cell_count_and_the_jsonl_at_startup(tmp_path, study, capsys):
        main(STUDY, CELLS, parse(tmp_path, []))
        assert "32 cells; auth api-key; writing " in capsys.readouterr().err


def describe_banked_runs():
    def it_runs_each_cell_up_to_n_counting_prior_successes():
        three = CELLS[:3]
        prior = Counter({cell_key(three[0]): 3, cell_key(three[1]): 5})
        runs = Counter(cell_name(cell) for _, cell in schedule(three, n=5, prior=prior))
        assert runs == {cell_name(three[0]): 2, cell_name(three[2]): 5}

    def it_drops_a_cell_out_of_the_round_robin_once_it_reaches_its_target():
        three = CELLS[:3]
        prior = Counter({cell_key(three[0]): 3})
        runs = list(schedule(three, n=5, prior=prior))
        assert [r for r, _ in runs] == [1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5]

    def it_counts_the_completed_runs_banked_under_output_per_full_cell(tmp_path, study):
        opus, sonnet = (next(cell for cell in CELLS if cell["model"] == model) for model in MODELS)
        bank(tmp_path, [(opus, 0), (opus, 1), (opus, 137), (sonnet, 0), (opus, 0)])
        main(STUDY, CELLS, parse(tmp_path, []))
        assert study.call_args.kwargs["prior"] == {cell_key(opus): 2, cell_key(sonnet): 1}

    def it_ignores_other_studies_and_runs_whose_result_is_an_error(tmp_path, study):
        opus = CELLS[0]
        bank(tmp_path, [(opus, 0)], study="v2-model-effort")
        banked_run(tmp_path, "20261012T000009Z_00000009", opus, result=CREDIT)
        banked_run(tmp_path, "20261012T000008Z_00000008", opus)
        main(STUDY, CELLS, parse(tmp_path, []))
        assert study.call_args.kwargs["prior"] == {cell_key(opus): 1}

    def it_starts_from_zero_when_output_does_not_exist_yet(tmp_path, study):
        main(STUDY, CELLS, parse(tmp_path, []))
        assert study.call_args.kwargs["prior"] == Counter()

    def it_prints_each_cell_s_shortfall_and_the_total(tmp_path, study, capsys):
        opus = CELLS[0]
        bank(tmp_path, [(opus, 0)] * 5)
        main(STUDY, CELLS, parse(tmp_path, []))
        err = capsys.readouterr().err
        assert f"{cell_name(opus)}=7" in err
        assert "total 379" in err


def describe_runs():
    def it_stops_submitting_after_n_runs_in_round_robin_order(tmp_path, gbnf_experiment):
        out = tmp_path / "matrix.jsonl"
        run_study(STUDY, CELLS, n=2, parallel=2, api_key=API_KEY, log=out, output=tmp_path / "runs", runs=5)
        lines = read(out)
        assert len(lines) == 5
        assert {line["round"] for line in lines} == {1}

    def it_passes_runs_from_the_command_line(tmp_path, study):
        main(STUDY, CELLS, parse(tmp_path, ["--runs", "4"]))
        assert study.call_args.kwargs["runs"] == 4

    def it_is_unlimited_by_default(tmp_path, study):
        main(STUDY, CELLS, parse(tmp_path, []))
        assert study.call_args.kwargs["runs"] is None


def describe_record():
    def it_writes_utc_start_and_finish_times(tmp_path, gbnf_experiment):
        out = tmp_path / "matrix.jsonl"
        run_study(STUDY, CELLS[:1], n=1, parallel=1, api_key=API_KEY, log=out, output=tmp_path / "runs")
        [line] = read(out)
        started, finished = (datetime.fromisoformat(line[key]) for key in ("started_at", "finished_at"))
        assert started.utcoffset().total_seconds() == 0
        assert started <= finished

    def it_writes_the_terminal_reason_and_the_first_300_characters_of_the_result(tmp_path, gbnf_experiment):
        gbnf_experiment.return_value = failed_run(
            tmp_path, "long", {"is_error": False, "terminal_reason": "completed", "result": "x" * 1000}
        )
        out = tmp_path / "matrix.jsonl"
        run_study(STUDY, CELLS[:1], n=1, parallel=1, api_key=API_KEY, log=out, output=tmp_path / "runs")
        [line] = read(out)
        assert line["terminal_reason"] == "completed"
        assert line["result"] == "x" * 300

    def it_writes_none_without_a_result_json(tmp_path, gbnf_experiment):
        gbnf_experiment.return_value = failed_run(tmp_path, "none")
        out = tmp_path / "matrix.jsonl"
        run_study(STUDY, CELLS[:1], n=1, parallel=1, api_key=API_KEY, log=out, output=tmp_path / "runs")
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
        stopped = run_study(STUDY, CELLS, n=2, parallel=1, api_key=API_KEY, log=out, output=tmp_path / "runs")
        [line] = read(out)
        assert stopped == line
        assert f"STOPPED: round 1 {cell_name(line['cell'])} {exhausted}: " in capsys.readouterr().err

    def it_lets_the_in_flight_runs_finish_and_names_the_first(tmp_path, gbnf_experiment, capsys):
        gbnf_experiment.return_value = failed_run(tmp_path, "exhausted", CREDIT)
        out = tmp_path / "matrix.jsonl"
        stopped = run_study(STUDY, CELLS, n=2, parallel=4, api_key=API_KEY, log=out, output=tmp_path / "runs")
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
        assert run_study(STUDY, CELLS, n=1, parallel=2, api_key=API_KEY, log=out, output=tmp_path / "runs") is None
        assert len(read(out)) == 32

    def it_exits_non_zero_when_stopped(tmp_path, study):
        study.return_value = {"round": 1}
        with pytest.raises(SystemExit) as exit:
            main(STUDY, CELLS, parse(tmp_path, []))
        assert exit.value.code != 0


def describe_auth():
    def it_gives_each_agent_no_key_on_subscription(tmp_path, gbnf_experiment, claude_agent):
        run_study(STUDY, CELLS[:1], n=1, parallel=1, api_key=None, log=tmp_path / "m", output=tmp_path / "runs")
        assert claude_agent.call_args.kwargs["api_key"] is None

    def it_passes_no_key_on_subscription(tmp_path, monkeypatch, study):
        monkeypatch.delenv("ANTHROPIC_API_KEY")
        main(STUDY, CELLS, parse(tmp_path, ["--auth", "subscription"]))
        assert study.call_args.kwargs["api_key"] is None

    def it_refuses_subscription_while_an_api_key_is_set(tmp_path, study):
        with pytest.raises(SystemExit) as exit:
            main(STUDY, CELLS, parse(tmp_path, ["--auth", "subscription"]))
        assert "ANTHROPIC_API_KEY" in str(exit.value.code)
        study.assert_not_called()

    @pytest.mark.parametrize("auth", ["api-key", "subscription"])
    def it_names_the_auth_mode_at_startup(auth, tmp_path, monkeypatch, study, capsys):
        if auth == "subscription":
            monkeypatch.delenv("ANTHROPIC_API_KEY")
        main(STUDY, CELLS, parse(tmp_path, ["--auth", auth]))
        assert f"auth {auth}" in capsys.readouterr().err
