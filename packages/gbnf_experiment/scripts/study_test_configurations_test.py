from unittest.mock import patch

import pytest
from study import cell_name
from study_test_configurations import cells, main


@pytest.fixture
def study(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    with patch("study.run_study", autospec=True) as m:
        m.return_value = None
        yield m


def describe_cells():
    def it_is_both_directions_by_every_test_flag_combination():
        assert len(cells()) == 2 * 8
        assert len({cell_name(cell) for cell in cells()}) == 16

    def it_is_opus_at_medium_effort():
        assert {(cell["model"], cell["effort"]) for cell in cells()} == {("claude-opus-5-5", "medium")}


def describe_main():
    def it_runs_the_sixteen_cells_as_v2_test_configurations_for_twelve_rounds_by_default(study):
        main([])
        assert study.call_args.args == ("v2-test-configurations", cells())
        assert study.call_args.kwargs["n"] == 12

    def it_takes_the_shared_flags(study):
        main(["--n", "3", "-k", "2", "--runs", "5"])
        assert (study.call_args.kwargs["n"], study.call_args.kwargs["parallel"], study.call_args.kwargs["runs"]) == (
            3,
            2,
            5,
        )
