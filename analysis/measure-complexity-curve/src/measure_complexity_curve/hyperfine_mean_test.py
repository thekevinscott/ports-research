import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from measure_complexity_curve.hyperfine_mean import hyperfine_mean


def export_json_flag(argv):
    return argv[argv.index("--export-json") + 1]


@pytest.fixture
def subprocess_module():
    def run(argv, **kwargs):
        Path(export_json_flag(argv)).write_text(json.dumps({"results": [{"mean": 0.05}]}))
        return Mock(returncode=0, stderr="")

    with patch("measure_complexity_curve.hyperfine_mean.subprocess", autospec=True) as m:
        m.run.side_effect = run
        yield m


def describe_hyperfine_mean():
    def it_returns_the_mean_hyperfine_reported(subprocess_module, tmp_path):
        assert hyperfine_mean(command="echo hi", scratch=tmp_path) == pytest.approx(0.05)

    def it_runs_hyperfine_against_the_given_command(subprocess_module, tmp_path):
        hyperfine_mean(command="echo hi", scratch=tmp_path)
        argv = subprocess_module.run.call_args.args[0]
        assert argv[0] == "hyperfine"
        assert argv[-1] == "echo hi"

    def it_raises_when_hyperfine_never_produced_a_report(tmp_path):
        with patch("measure_complexity_curve.hyperfine_mean.subprocess", autospec=True) as m:
            m.run.return_value = Mock(returncode=1, stderr="boom")
            with pytest.raises(RuntimeError):
                hyperfine_mean(command="echo hi", scratch=tmp_path)
