import json
import os
import subprocess
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def run_cli(*args: str) -> str:
    """The installed entry point as a real subprocess: the CLI is the whole public surface."""
    result = subprocess.run(
        ["uv", "run", "exercise-api", *args],
        cwd=PACKAGE_ROOT,
        env=os.environ,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


def compare(language: str, reference: Path, target: Path, cases: Path, *extra: str) -> dict:
    report = json.loads(run_cli("--language", language, "--reference", str(reference), "--target", str(target), "--cases", str(cases), *extra))
    return report["targets"][str(target)]


def _print(capsys, label: str, target: dict) -> None:
    with capsys.disabled():
        print(
            f"\n{label}: cases={target['cases']} agree={target['agree_with_reference']} "
            f"reference_errors={target['reference_error_cases']} target_errors={target['target_error_cases']} "
            f"reference_p50_ns={target['reference_p50_elapsed_ns']} target_p50_ns={target['target_p50_elapsed_ns']}"
        )


LADDER_CASES = 22
# The top of each series is past what a reference can do: python raises RecursionError on
# five of them and MemoryError on nested depth 8192, typescript RangeError on three.
LADDER_REFERENCE_ERRORS = {"python": 6, "typescript": 3}


def _print_ladder(capsys, label: str, target: dict) -> None:
    with capsys.disabled():
        print(f"\n{label}: rung, input_len, construct_ms, add_ms")
        for entry in target["timings"]:
            print(
                f"  {entry['rung']:20} {entry['input_len']:6} "
                f"{entry['construct_ns']['median'] / 1e6:10.4f} {entry['add_ns']['median'] / 1e6:10.4f} "
                f"spread={entry['add_ns']['spread']:.3f}"
            )


def describe_exercise_api_against_kevins_references():
    def it_finds_the_python_reference_agrees_with_itself_on_generated_cases(python_reference, generated_cases, capsys):
        target = compare("python", python_reference, python_reference, generated_cases)
        _print(capsys, "python/generated", target)
        assert target["cases"] == 500
        assert target["agree_with_reference"] == 500
        assert 0 < target["reference_error_cases"] < 500

    def it_finds_the_typescript_reference_agrees_with_itself_on_generated_cases(typescript_reference, generated_cases, capsys):
        target = compare("typescript", typescript_reference, typescript_reference, generated_cases)
        _print(capsys, "typescript/generated", target)
        assert target["cases"] == 500
        assert target["agree_with_reference"] == 500
        assert 0 < target["reference_error_cases"] < 500

    def it_finds_the_python_reference_accepts_every_fixture_case(python_reference, fixture_cases, capsys):
        target = compare("python", python_reference, python_reference, fixture_cases)
        _print(capsys, "python/fixtures", target)
        assert target["cases"] == 453
        assert target["reference_error_cases"] == 0

    def it_finds_the_typescript_reference_accepts_every_fixture_case(typescript_reference, fixture_cases, capsys):
        target = compare("typescript", typescript_reference, typescript_reference, fixture_cases)
        _print(capsys, "typescript/fixtures", target)
        assert target["cases"] == 453
        assert target["reference_error_cases"] == 0

    def it_runs_the_ladder_on_the_python_reference(python_reference, ladder_cases, capsys):
        target = compare("python", python_reference, python_reference, ladder_cases)
        _print_ladder(capsys, "python/ladder", target)
        errors = LADDER_REFERENCE_ERRORS["python"]
        assert target["cases"] == LADDER_CASES
        assert target["reference_error_cases"] == errors
        assert len(target["timings"]) == LADDER_CASES - errors

    def it_runs_the_ladder_on_the_typescript_reference(typescript_reference, ladder_cases, capsys):
        target = compare("typescript", typescript_reference, typescript_reference, ladder_cases)
        _print_ladder(capsys, "typescript/ladder", target)
        errors = LADDER_REFERENCE_ERRORS["typescript"]
        assert target["cases"] == LADDER_CASES
        assert target["reference_error_cases"] == errors
        assert len(target["timings"]) == LADDER_CASES - errors

    def it_regenerates_the_committed_ladder_file_byte_for_byte(grammars_dir, ladder_cases, tmp_path):
        out = tmp_path / "ladder.jsonl"
        run_cli("ladder", "--grammars", str(grammars_dir), "--out", str(out))
        assert out.read_text() == ladder_cases.read_text()

    def it_rebuilds_the_committed_fixture_file_from_the_derivation(grammars_dir, fixture_cases, tmp_path):
        out = tmp_path / "fixtures.jsonl"
        run_cli("fixtures", "--grammars", str(grammars_dir), "--out", str(out))
        assert out.read_text() == fixture_cases.read_text()


def describe_exercise_api_against_one_real_port():
    def it_runs_a_python_port_through_the_adapt_shim(python_reference, python_port, generated_cases, capsys):
        target = compare("python", python_reference, python_port, generated_cases, "--adapt")
        _print(capsys, "python/port 9f286468", target)
        assert target["cases"] == 500
        assert target["agree_with_reference"] + target["disagree_with_reference"] == 500

    def it_runs_a_typescript_port_through_the_adapt_shim(typescript_reference, typescript_port, generated_cases, capsys):
        target = compare("typescript", typescript_reference, typescript_port, generated_cases, "--adapt")
        _print(capsys, "typescript/port 1c28aa33", target)
        assert target["cases"] == 500
        assert target["agree_with_reference"] + target["disagree_with_reference"] == 500
