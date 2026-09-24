import json
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from gbnf_experiment.prepare_filesystem.write_manifest import write_manifest

ROOT = Path("/pkg/gbnf-experiment")
IMAGE_ID = "sha256:" + "b" * 64
HEAD = "c" * 40

CONDITION = {
    "name": "source-typescript_python-tests_effort-high_model-claude-opus-5",
    "source_language": "typescript",
    "target_language": "python",
    "include_typescript_tests": False,
    "include_python_tests": True,
    "effort": "high",
    "model": "claude-opus-5",
}
PATTERNS = ("/package.json", "/src/*.ts", "!**/*.test.ts")
INCLUDED = ("package.json", "src/gbnf.ts")
CALL = {
    "timestamp": datetime(2026, 9, 6, 14, 25, 30, tzinfo=UTC),
    "condition": CONDITION,
    "patterns": PATTERNS,
    "included": INCLUDED,
    "image_tag": "agent-harness-sandbox-claude:latest",
    "gbnf_commit": "13f1aca",
}


@pytest.fixture
def settings():
    with patch("gbnf_experiment.prepare_filesystem.write_manifest.settings", autospec=True) as m:
        m.root_directory = ROOT
        yield m


@pytest.fixture
def git_stdout():
    return {"rev-parse": HEAD + "\n", "status": ""}


@pytest.fixture
def subprocess_module(settings, git_stdout):
    with patch("gbnf_experiment.prepare_filesystem.write_manifest.subprocess", autospec=True) as m:
        m.run.side_effect = lambda argv, **kwargs: Mock(stdout=git_stdout[argv[3]])
        yield m


@pytest.fixture
def docker_module():
    with patch("gbnf_experiment.prepare_filesystem.write_manifest.docker", autospec=True) as m:
        m.image.inspect.return_value.id = IMAGE_ID
        yield m


@pytest.fixture
def run_directory(tmp_path):
    directory = tmp_path / "20260906T142530Z_9f2b1c04"
    directory.mkdir()
    return directory


@pytest.fixture
def written(run_directory, subprocess_module, docker_module):
    def write(**overrides) -> str:
        write_manifest(run_directory, **{**CALL, **overrides})
        return (run_directory / "manifest.json").read_text()

    return write


@pytest.fixture
def manifest(written):
    def read(**overrides) -> dict:
        return json.loads(written(**overrides))

    return read


def describe_write_manifest():
    def it_writes_manifest_json_into_the_run_directory(run_directory, written):
        written()
        assert [path.name for path in run_directory.iterdir()] == ["manifest.json"]

    def it_returns_nothing(run_directory, subprocess_module, docker_module):
        assert write_manifest(run_directory, **CALL) is None

    def it_writes_the_four_sections_beside_the_timestamps(manifest):
        assert list(manifest()) == [
            "timestamp",
            "completed_at",
            "condition",
            "derivation",
            "reference_implementation",
            "sandbox",
            "harness",
        ]

    def it_stamps_the_timestamp_in_basic_utc(manifest):
        assert manifest()["timestamp"] == "2026-09-06T14:25:30Z"

    def it_normalises_a_non_utc_timestamp(manifest):
        stamp = datetime(2026, 9, 6, 9, 25, 30, tzinfo=timezone(timedelta(hours=-5)))
        assert manifest(timestamp=stamp)["timestamp"] == "2026-09-06T14:25:30Z"

    def it_records_the_condition_it_was_given(manifest):
        assert manifest()["condition"] == CONDITION

    def it_records_the_error_it_was_given(manifest):
        assert manifest(error="the container died")["error"] == "the container died"

    def it_records_the_pinned_commit(manifest):
        assert manifest()["derivation"] == {"gbnf_commit": "13f1aca"}

    def it_records_the_whitelist_the_reference_was_assembled_from(manifest):
        assert manifest()["reference_implementation"]["patterns"] == [
            "/package.json",
            "/src/*.ts",
            "!**/*.test.ts",
        ]

    def it_names_every_included_path(manifest):
        assert manifest()["reference_implementation"]["included"] == [
            "package.json",
            "src/gbnf.ts",
        ]

    def it_counts_what_the_whitelist_admitted(manifest):
        assert manifest()["reference_implementation"]["included_count"] == 2

    def it_identifies_the_sandbox_by_image_id_not_by_tag(manifest):
        assert manifest()["sandbox"] == {"image_id": IMAGE_ID}

    def it_inspects_the_tag_it_was_given(written, docker_module):
        written(image_tag="agent-harness-sandbox-pi:latest")
        docker_module.image.inspect.assert_called_once_with(
            "agent-harness-sandbox-pi:latest"
        )

    def it_records_one_commit_for_the_whole_harness(manifest):
        assert manifest()["harness"]["commit"] == HEAD

    def it_reports_a_clean_working_tree(manifest):
        assert manifest()["harness"]["dirty"] is False

    def it_flags_an_uncommitted_working_tree(manifest, git_stdout):
        git_stdout["status"] = " M src/gbnf_experiment/config.py\n"
        assert manifest()["harness"]["dirty"] is True

    def it_reads_git_against_the_harness_root(written, subprocess_module):
        written()
        assert [call.args[0] for call in subprocess_module.run.call_args_list] == [
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            ["git", "-C", str(ROOT), "status", "--porcelain"],
        ]

    def it_raises_when_git_exits_nonzero(written, subprocess_module):
        subprocess_module.run.side_effect = RuntimeError("not a git checkout")
        with pytest.raises(RuntimeError):
            written()

    def it_writes_it_readably(written):
        assert written().splitlines()[1] == '  "timestamp": "2026-09-06T14:25:30Z",'

    def it_ends_with_a_newline(written):
        assert written().endswith("\n")
