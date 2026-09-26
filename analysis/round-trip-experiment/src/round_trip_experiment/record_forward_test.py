import json
from pathlib import Path

import pytest

from round_trip_experiment.record_forward import record_forward

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


@pytest.fixture
def reverse_run(tmp_path: Path) -> Path:
    directory = tmp_path / "reverse" / "20260909T001426Z_1c28aa33" / "20260909T021103Z_9f0a1b2c"
    directory.mkdir(parents=True)
    (directory / "manifest.json").write_text(json.dumps(HARNESS_MANIFEST, indent=2) + "\n")
    return directory


def record(reverse_run: Path) -> dict:
    return record_forward(
        reverse_run,
        run_id="20260909T001426Z_1c28aa33",
        condition=FORWARD_CONDITION,
    )


def describe_record_forward():
    def it_leaves_the_keys_the_harness_wrote_untouched(reverse_run):
        record(reverse_run)
        written = json.loads((reverse_run / "manifest.json").read_text())
        assert {key: written[key] for key in HARNESS_MANIFEST} == HARNESS_MANIFEST

    def it_names_the_forward_run_it_came_from(reverse_run):
        record(reverse_run)
        written = json.loads((reverse_run / "manifest.json").read_text())
        assert written["forward"]["run_id"] == "20260909T001426Z_1c28aa33"

    def it_records_the_forward_condition_verbatim(reverse_run):
        record(reverse_run)
        written = json.loads((reverse_run / "manifest.json").read_text())
        assert written["forward"]["condition"] == FORWARD_CONDITION

    def it_returns_the_amended_manifest(reverse_run):
        assert record(reverse_run) == json.loads((reverse_run / "manifest.json").read_text())

    def it_keeps_the_harnesss_formatting(reverse_run):
        record(reverse_run)
        text = (reverse_run / "manifest.json").read_text()
        assert text.endswith("}\n")
        assert '\n  "forward": {' in text

    def it_is_idempotent_on_a_second_call(reverse_run):
        record(reverse_run)
        once = (reverse_run / "manifest.json").read_text()
        record(reverse_run)
        assert (reverse_run / "manifest.json").read_text() == once

    def it_fails_when_the_harness_wrote_no_manifest(tmp_path):
        with pytest.raises(FileNotFoundError):
            record_forward(tmp_path, run_id="20260909T001426Z_1c28aa33", condition=FORWARD_CONDITION)
