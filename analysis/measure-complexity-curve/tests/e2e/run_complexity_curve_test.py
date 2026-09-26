import json
import os
import subprocess
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]

SWEEP = ["--max-size", "64", "--steps", "5", "--nesting-depth", "1", "--alternation-width", "2", "--iterations", "100", "--seed", "0"]


def run_cli(language: str, target: Path) -> dict:
    """The installed entry point, driven as a real subprocess — the CLI is the
    whole public surface of this package, and this is the only tier that
    exercises it rather than the functions behind it."""
    result = subprocess.run(
        ["uv", "run", "measure-complexity-curve", "--language", language, "--target", str(target), *SWEEP],
        cwd=PACKAGE_ROOT,
        env=os.environ,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def describe_measure_complexity_curve():
    def it_fingerprints_kevins_python_reference(python_reference, capsys):
        report = run_cli("python", python_reference)

        assert report["curve"][0]["size"] == 4
        assert report["curve"][-1]["size"] == 64
        assert len(report["curve"]) == 5
        assert isinstance(report["log_log_slope"], float)
        with capsys.disabled():
            print(f"\npython reference log-log slope: {report['log_log_slope']}")

    def it_fingerprints_kevins_typescript_reference(typescript_reference, capsys):
        report = run_cli("typescript", typescript_reference)

        assert report["curve"][0]["size"] == 4
        assert report["curve"][-1]["size"] == 64
        assert len(report["curve"]) == 5
        assert isinstance(report["log_log_slope"], float)
        with capsys.disabled():
            print(f"\ntypescript reference log-log slope: {report['log_log_slope']}")
