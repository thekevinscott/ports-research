import json
from concurrent.futures import ThreadPoolExecutor
from itertools import islice
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner
from run_matrix import MODELS, cell_name, cells, cli, run_matrix, schedule

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


@pytest.fixture
def gbnf_experiment(run_directory):
    with patch("run_matrix.run_gbnf_experiment", autospec=True) as m:
        m.return_value = run_directory
        yield m


@pytest.fixture(autouse=True)
def claude_agent():
    with patch("run_matrix.ClaudeAgent", autospec=True) as m:
        yield m


@pytest.fixture(autouse=True)
def prepare():
    with patch("run_matrix.prepare_reference_implementation", autospec=True) as m:
        yield m


@pytest.fixture(autouse=True)
def threads():
    # Mocks do not cross a process boundary, and only the main thread may set a signal handler.
    with patch("run_matrix.ProcessPoolExecutor", lambda parallel, **_: ThreadPoolExecutor(parallel)):
        yield


def read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def describe_cells():
    def it_is_directions_by_test_flags_by_models():
        assert len(cells()) == 2 * 8 * 4
        assert len({cell_name(cell) for cell in cells()}) == 64

    def it_covers_every_model():
        assert {cell["model"] for cell in cells()} == set(MODELS)

    def it_leaves_effort_to_the_cli_by_default():
        assert {cell["effort"] for cell in cells()} == {None}

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


def describe_run_matrix():
    def it_writes_one_line_per_run(tmp_path, gbnf_experiment):
        out = tmp_path / "matrix.jsonl"
        run_matrix(cells(), n=2, parallel=2, api_key=API_KEY, out=out)
        assert len(read(out)) == 128

    def it_writes_the_cell_round_run_directory_exit_code_wall_time_and_usage(
        tmp_path, gbnf_experiment, run_directory
    ):
        out = tmp_path / "matrix.jsonl"
        [cell] = cells(efforts=("high",))[:1]
        run_matrix([cell], n=1, parallel=1, api_key=API_KEY, out=out)
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
        run_matrix(cells(), n=1, parallel=1, api_key=API_KEY, out=out)
        lines = read(out)
        assert len(lines) == 64
        assert lines[0]["error"] == "boom"
        assert lines[0]["run_directory"] is None
        assert all(line["error"] is None for line in lines[1:])

    def it_writes_runs_in_round_order(tmp_path, gbnf_experiment):
        out = tmp_path / "matrix.jsonl"
        run_matrix(cells(), n=2, parallel=1, api_key=API_KEY, out=out)
        rounds = [line["round"] for line in read(out)]
        assert rounds == [1] * 64 + [2] * 64

    def it_gives_each_agent_the_key_and_its_cell_s_model_and_effort(
        tmp_path, gbnf_experiment, claude_agent
    ):
        two = [cell for cell in cells(efforts=("low", "xhigh")) if cell_name(cell) in NAMES]
        run_matrix(two, n=1, parallel=1, api_key=API_KEY, out=tmp_path / "m")
        assert sorted(c.kwargs["effort"] for c in claude_agent.call_args_list) == ["low", "xhigh"]
        for c in claude_agent.call_args_list:
            assert c.kwargs == {"model": MODELS[0], "effort": c.kwargs["effort"], "api_key": API_KEY}

    def it_warms_every_condition_before_the_first_run(tmp_path, gbnf_experiment, prepare):
        order = Mock()
        order.attach_mock(prepare, "prepare")
        order.attach_mock(gbnf_experiment, "run")
        run_matrix(cells(), n=1, parallel=2, api_key=API_KEY, out=tmp_path / "m")
        names = [name for name, _, _ in order.mock_calls]
        assert names[:16] == ["prepare"] * 16
        assert "prepare" not in names[16:]


def describe_cli():
    @pytest.mark.parametrize("environment", [{}, {"ANTHROPIC_API_KEY": ""}])
    def it_refuses_to_start_without_an_api_key(
        environment, monkeypatch, gbnf_experiment, prepare, claude_agent
    ):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        result = CliRunner().invoke(cli, ["--n", "1"], env=environment)
        assert result.exit_code != 0
        assert "ANTHROPIC_API_KEY" in result.output
        prepare.assert_not_called()
        gbnf_experiment.assert_not_called()
        claude_agent.assert_not_called()

    def it_runs_every_cell_at_every_effort_given(monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", API_KEY)
        with patch("run_matrix.run_matrix", autospec=True) as matrix:
            result = CliRunner().invoke(cli, ["--efforts", "low,xhigh"])
        assert result.exit_code == 0, result.output
        selected = matrix.call_args.args[0]
        assert len(selected) == 128
        assert {cell["effort"] for cell in selected} == {"low", "xhigh"}

    def it_selects_cells_by_name_including_effort(monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", API_KEY)
        with patch("run_matrix.run_matrix", autospec=True) as matrix:
            CliRunner().invoke(cli, ["--efforts", "low,xhigh", "--cells", NAMES[1]])
        [cell] = matrix.call_args.args[0]
        assert cell["effort"] == "xhigh"
