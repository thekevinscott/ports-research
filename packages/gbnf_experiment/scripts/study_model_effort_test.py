from unittest.mock import patch

import pytest
from study import cell_name
from study_model_effort import EFFORTS, MODELS, cells, main


@pytest.fixture
def study(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    with patch("study.run_study", autospec=True) as m:
        m.return_value = None
        yield m


def describe_cells():
    def it_is_both_directions_by_every_model_by_every_effort():
        assert len(cells()) == 2 * 4 * 5
        assert len({cell_name(cell) for cell in cells()}) == 40

    def it_covers_every_model_at_every_effort():
        assert {(cell["model"], cell["effort"]) for cell in cells()} == set(
            (model, effort) for model in MODELS for effort in EFFORTS
        )

    def it_includes_medium():
        assert "medium" in EFFORTS

    def it_runs_unit_and_source_integration_tests_only():
        assert {
            (cell["include_unit_tests"], cell["include_source_integration_tests"], cell["include_target_integration_tests"])
            for cell in cells()
        } == {(True, True, False)}


def describe_main():
    def it_runs_the_forty_cells_as_v2_model_effort_for_twelve_rounds_by_default(tmp_path, study):
        main(["--output", str(tmp_path)])
        assert study.call_args.args == ("v2-model-effort", cells())
        assert study.call_args.kwargs["n"] == 12

    def it_requires_an_output_directory(study):
        with pytest.raises(SystemExit):
            main([])
        study.assert_not_called()

    def it_takes_the_shared_flags(tmp_path, study):
        main(["--output", str(tmp_path), "--n", "3", "-k", "2", "--runs", "5"])
        assert (study.call_args.kwargs["n"], study.call_args.kwargs["parallel"], study.call_args.kwargs["runs"]) == (
            3,
            2,
            5,
        )
