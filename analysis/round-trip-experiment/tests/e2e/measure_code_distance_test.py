import json
import os
import subprocess
from itertools import chain
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DISTANCES = {"token_levenshtein", "token_levenshtein_raw", "char_levenshtein"}


def run_cli(language: str, a: Path, b: Path, exclude: list[str]) -> dict:
    result = subprocess.run(
        [
            "uv", "run", "measure-code-distance", "levenshtein", "--language", language, "--a", str(a), "--b", str(b),
            *chain.from_iterable(("--exclude", pattern) for pattern in exclude),
        ],
        cwd=PACKAGE_ROOT,
        env=os.environ,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def describe_measure_code_distance():
    def it_measures_the_python_reference_against_itself_as_zero(python_reference, exclude_by_language, capsys):
        report = run_cli("python", python_reference, python_reference, exclude_by_language["python"])
        assert {report[field] for field in DISTANCES} == {0.0}
        assert report["file_count_a"] > 0
        with capsys.disabled():
            print(f"\npython reference vs itself: {json.dumps(report)}")

    def it_measures_the_typescript_reference_against_itself_as_zero(typescript_reference, exclude_by_language, capsys):
        report = run_cli("typescript", typescript_reference, typescript_reference, exclude_by_language["typescript"])
        assert {report[field] for field in DISTANCES} == {0.0}
        assert report["file_count_a"] > 0
        with capsys.disabled():
            print(f"\ntypescript reference vs itself: {json.dumps(report)}")

    def it_measures_a_banked_port_against_the_reference_of_its_target_language(
        run_directory, python_reference, typescript_reference, exclude_by_language, capsys
    ):
        language = json.loads((run_directory / "manifest.json").read_text())["condition"]["target_language"]
        reference = {"python": python_reference, "typescript": typescript_reference}[language]
        report = run_cli(language, reference, run_directory / "ported_implementation", exclude_by_language[language])
        assert all(0.0 <= report[field] <= 1.0 for field in DISTANCES)
        assert report["file_count_b"] > 0
        with capsys.disabled():
            print(f"\n{run_directory.name} vs {language} reference: {json.dumps(report)}")
