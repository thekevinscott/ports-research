import json
import os
import subprocess
from itertools import chain
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
FIELDS = {
    "language",
    "target",
    "parsed_file_count",
    "node_count",
    "max_depth",
    "function_count",
    "mean_function_lines",
    "max_function_lines",
    "mean_cyclomatic",
    "max_cyclomatic",
}


def run_cli(language: str, target: Path, exclude: list[str]) -> dict:
    result = subprocess.run(
        [
            "uv", "run", "measure-ast", "--language", language, "--target", str(target),
            *chain.from_iterable(("--exclude", pattern) for pattern in exclude),
        ],
        cwd=PACKAGE_ROOT,
        env=os.environ,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def describe_measure_ast():
    def it_measures_kevins_python_reference(python_reference, exclude_by_language, capsys):
        report = run_cli("python", python_reference, exclude_by_language["python"])
        assert set(report) == FIELDS
        assert report["parsed_file_count"] > 0
        with capsys.disabled():
            print(f"\npython reference: {json.dumps(report)}")

    def it_measures_kevins_typescript_reference(typescript_reference, exclude_by_language, capsys):
        report = run_cli("typescript", typescript_reference, exclude_by_language["typescript"])
        assert set(report) == FIELDS
        assert report["parsed_file_count"] > 0
        with capsys.disabled():
            print(f"\ntypescript reference: {json.dumps(report)}")
