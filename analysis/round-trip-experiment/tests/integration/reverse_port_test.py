import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
GBNF_EXPERIMENT_ROOT = PACKAGE_ROOT.parents[1] / "packages" / "gbnf-experiment"
DERIVATION_KEY = "af673dbe41be73ce"
UV = shutil.which("uv")
FORWARD_CONDITION = {
    "name": "source-python_python-tests_effort-high_model-claude-opus-5",
    "source_language": "python",
    "target_language": "typescript",
    "include_python_tests": True,
    "include_typescript_tests": False,
    "effort": "high",
    "model": "claude-opus-5",
}
HARNESS_MANIFEST = {
    "timestamp": "2026-09-09T02:11:03Z",
    "completed_at": "2026-09-09T02:29:41Z",
    "condition": {
        "name": "source-typescript_typescript-tests_python-tests_effort-high_model-claude-opus-5",
        "source_language": "typescript",
        "target_language": "python",
        "include_python_tests": True,
        "include_typescript_tests": True,
        "effort": "high",
        "model": "claude-opus-5",
    },
    "derivation": {"gbnf_commit": "13f1aca495d11e160fffd68c4ba299a2415909d8"},
    "sandbox": {"image_id": "sha256:abc"},
    "harness": {"commit": "7429f13", "dirty": False},
}


def assistant(message_id: str, **usage) -> str:
    return json.dumps({"type": "assistant", "message": {"id": message_id, "usage": usage}})


@pytest.fixture
def places(tmp_path):
    root = tmp_path.resolve()
    return {
        "derivations": root / "gbnf-cache" / "derivations",
        "staging": root / "round-trip-cache" / "derivations",
        "reverse": root / "reverse",
    }


@pytest.fixture
def derivation_cache(places):
    for language in ("python", "typescript"):
        suite = places["derivations"] / DERIVATION_KEY / "tests" / language
        suite.mkdir(parents=True)
        (suite / "keep.txt").write_text("suite\n")
    return places["derivations"]


@pytest.fixture
def env(places):
    return {
        **os.environ,
        "GBNF_EXPERIMENT_PREPARED_DIRECTORY": str(places["derivations"]),
        "ROUND_TRIP_EXPERIMENT_STAGING_DIRECTORY": str(places["staging"]),
        "ROUND_TRIP_EXPERIMENT_REVERSE_DIRECTORY": str(places["reverse"]),
    }


@pytest.fixture
def forward_run(tmp_path):
    directory = tmp_path.resolve() / "20260909T001426Z_1c28aa33"
    port = directory / "ported_implementation"
    (port / "src").mkdir(parents=True)
    (port / "src" / "index.ts").write_text("export const f = () => 1;\n")
    (port / "node_modules" / "left-pad").mkdir(parents=True)
    (port / "node_modules" / "left-pad" / "index.js").write_text("module.exports = 1;\n")
    (directory / "manifest.json").write_text(json.dumps({"condition": FORWARD_CONDITION}))
    (directory / "result.json").write_text(json.dumps({"is_error": False, "duration_ms": 456517}))
    transcript = directory / "transcript" / "-workspace"
    transcript.mkdir(parents=True)
    (transcript / "session.jsonl").write_text(
        assistant("msg_a", input_tokens=10, cache_creation_input_tokens=100, cache_read_input_tokens=1000, output_tokens=5)
    )
    return directory


def run_cli(env, *args):
    return subprocess.run(
        [UV, "run", "reverse-port", *args],
        cwd=PACKAGE_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def staged_report(env, derivation_cache, forward_run):
    result = run_cli(env, "stage", "--run", str(forward_run))
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def describe_stage():
    def it_copies_the_port_in_as_the_reverse_source_languages_derived_source(staged_report, places, forward_run):
        staged = places["staging"] / forward_run.name / DERIVATION_KEY
        assert staged_report["staged"] == str(staged)
        assert (staged / "source" / "typescript" / "src" / "index.ts").read_text() == "export const f = () => 1;\n"

    def it_leaves_build_artefacts_out(staged_report, places, forward_run):
        staged = places["staging"] / forward_run.name / DERIVATION_KEY
        assert not (staged / "source" / "typescript" / "node_modules").exists()

    def it_links_the_real_test_suites_beside_the_source(staged_report, places, forward_run):
        staged = places["staging"] / forward_run.name / DERIVATION_KEY
        assert (staged / "tests").is_symlink()
        assert (staged / "tests" / "python" / "keep.txt").read_text() == "suite\n"

    def it_reverses_the_condition_with_both_suites(staged_report):
        assert staged_report["condition"] == {
            "source_language": "typescript",
            "include_typescript_tests": True,
            "include_python_tests": True,
            "effort": "high",
            "model": "claude-opus-5",
        }

    def it_prints_the_run_gbnf_experiment_command(staged_report):
        assert staged_report["argv"] == [
            "uv", "run", "--directory", str(GBNF_EXPERIMENT_ROOT), "run-gbnf-experiment",
            "--source-language", "typescript",
            "--include-typescript-tests",
            "--include-python-tests",
            "--effort", "high",
            "--model", "claude-opus-5",
        ]

    def it_points_the_harness_at_the_staged_derivation_and_the_forward_runs_reverse_root(
        staged_report, places, forward_run
    ):
        assert staged_report["env"] == {
            "GBNF_EXPERIMENT_PREPARED_DIRECTORY": str(places["staging"] / forward_run.name),
            "GBNF_EXPERIMENT_DATA_DIRECTORY": str(places["reverse"] / forward_run.name),
        }

    def it_estimates_the_leg_from_the_forward_runs_own_transcript(staged_report):
        assert staged_report["estimate"] == {"total_tokens": 1115, "api_calls": 1, "duration_ms": 456517}

    def it_names_the_forward_run_it_came_from(staged_report, forward_run):
        assert staged_report["forward"] == {"run_id": forward_run.name, "condition": FORWARD_CONDITION}

    def it_banks_nothing(staged_report, places):
        assert not places["reverse"].exists()

    def it_fails_with_a_message_when_the_run_has_no_port(env, derivation_cache, tmp_path):
        bare = tmp_path.resolve() / "20260909T001426Z_00000000"
        bare.mkdir()
        (bare / "manifest.json").write_text(json.dumps({"condition": FORWARD_CONDITION}))
        result = run_cli(env, "stage", "--run", str(bare))
        assert result.returncode != 0
        assert result.stdout == ""
        assert "ported_implementation" in result.stderr


def describe_record():
    @pytest.fixture
    def reverse_run(places, forward_run):
        directory = places["reverse"] / forward_run.name / "20260909T021103Z_9f0a1b2c"
        directory.mkdir(parents=True)
        (directory / "manifest.json").write_text(json.dumps(HARNESS_MANIFEST, indent=2) + "\n")
        return directory

    def it_adds_the_forward_run_to_the_manifest_the_harness_wrote(env, reverse_run, forward_run):
        result = run_cli(env, "record", "--run", str(reverse_run), "--forward", str(forward_run))
        assert result.returncode == 0, result.stderr
        written = json.loads((reverse_run / "manifest.json").read_text())
        assert {key: written[key] for key in HARNESS_MANIFEST} == HARNESS_MANIFEST
        assert written["forward"] == {"run_id": forward_run.name, "condition": FORWARD_CONDITION}

    def it_prints_the_amended_manifest(env, reverse_run, forward_run):
        result = run_cli(env, "record", "--run", str(reverse_run), "--forward", str(forward_run))
        assert json.loads(result.stdout) == json.loads((reverse_run / "manifest.json").read_text())

    def it_fails_with_a_message_when_the_harness_wrote_no_manifest(env, places, forward_run):
        empty = places["reverse"] / forward_run.name / "20260909T034500Z_0d0e0f10"
        empty.mkdir(parents=True)
        result = run_cli(env, "record", "--run", str(empty), "--forward", str(forward_run))
        assert result.returncode != 0
        assert "manifest.json" in result.stderr


def describe_run():
    @pytest.fixture
    def harness_stub(tmp_path):
        directory = tmp_path.resolve() / "bin"
        directory.mkdir()
        stub = directory / "uv"
        stub.write_text(
            "\n".join(
                [
                    f"#!{sys.executable}",
                    "import json, os, sys",
                    "from pathlib import Path",
                    "run = Path(os.environ['GBNF_EXPERIMENT_DATA_DIRECTORY']) / '20260909T021103Z_9f0a1b2c'",
                    "run.mkdir(parents=True)",
                    f"run.joinpath('manifest.json').write_text(json.dumps({HARNESS_MANIFEST!r}, indent=2) + chr(10))",
                    "run.joinpath('argv.json').write_text(json.dumps(sys.argv))",
                    "run.joinpath('env.json').write_text(json.dumps({k: v for k, v in os.environ.items() if k.startswith('GBNF_EXPERIMENT_')}))",
                ]
            )
            + "\n"
        )
        stub.chmod(0o755)
        return directory

    @pytest.fixture
    def stubbed_env(env, harness_stub):
        return {**env, "PATH": f"{harness_stub}{os.pathsep}{env['PATH']}"}

    @pytest.fixture
    def report(stubbed_env, derivation_cache, forward_run):
        result = run_cli(stubbed_env, "run", "--run", str(forward_run))
        assert result.returncode == 0, result.stdout + result.stderr
        return json.loads(result.stdout)

    def it_launches_the_harness_with_the_reverse_condition(report):
        argv = json.loads((Path(report["run_directory"]) / "argv.json").read_text())
        assert argv[1:] == report["argv"][1:]

    def it_launches_the_harness_against_the_staged_derivation(report, places, forward_run):
        launched = json.loads((Path(report["run_directory"]) / "env.json").read_text())
        assert launched["GBNF_EXPERIMENT_PREPARED_DIRECTORY"] == str(places["staging"] / forward_run.name)
        assert launched["GBNF_EXPERIMENT_DATA_DIRECTORY"] == str(places["reverse"] / forward_run.name)

    def it_banks_the_leg_under_the_forward_run(report, places, forward_run):
        assert report["run_directory"] == str(places["reverse"] / forward_run.name / "20260909T021103Z_9f0a1b2c")

    def it_records_the_forward_run_on_the_manifest_the_harness_wrote(report, forward_run):
        written = json.loads((Path(report["run_directory"]) / "manifest.json").read_text())
        assert {key: written[key] for key in HARNESS_MANIFEST} == HARNESS_MANIFEST
        assert written["forward"] == {"run_id": forward_run.name, "condition": FORWARD_CONDITION}

    def it_refuses_to_launch_when_the_staged_derivation_is_incomplete(stubbed_env, places, forward_run):
        result = run_cli(stubbed_env, "run", "--run", str(forward_run))
        assert result.returncode != 0
        assert "refusing to launch" in result.stderr
        assert "tests/python" in result.stderr
        assert not places["reverse"].exists()
