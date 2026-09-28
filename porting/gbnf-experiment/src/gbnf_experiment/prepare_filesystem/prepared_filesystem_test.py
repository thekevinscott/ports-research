import json
import re
from datetime import UTC
from unittest.mock import Mock, patch

import pytest

from gbnf_experiment.prepare_filesystem.prepared_filesystem import PreparedFilesystem

HEAD = "c" * 40
IMAGE_ID = "sha256:" + "b" * 64

AGENT = Mock(name="agent")
AGENT.image = "agent-harness-sandbox-claude:latest"

CONDITION = {
    "source_language": "typescript",
    "include_unit_tests": False,
    "include_source_integration_tests": False,
    "include_target_integration_tests": False,
    "effort": "high",
    "model": "claude-opus-5",
}
PROMPT = "Port the typescript implementation under /input/javascript"


@pytest.fixture
def settings(tmp_path):
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.settings", autospec=True
    ) as m:
        m.data_directory = tmp_path / "data"
        m.gbnf_commit = "13f1aca"
        yield m


@pytest.fixture
def reference(tmp_path):
    """What the prepare image copied out, standing in for a real build."""
    directory = tmp_path / "shared"
    (directory / "javascript" / "src").mkdir(parents=True)
    (directory / "javascript" / "src" / "index.ts").write_text("export {};")
    return directory


@pytest.fixture
def prepare_reference_implementation(reference):
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.prepare_reference_implementation",
        autospec=True,
    ) as m:
        m.return_value = reference
        yield m


@pytest.fixture
def git_stdout():
    return {"rev-parse": HEAD + "\n", "status": ""}


@pytest.fixture
def subprocess_module(settings, git_stdout):
    with patch(
        "gbnf_experiment.prepare_filesystem.write_manifest.subprocess", autospec=True
    ) as m:
        m.run.side_effect = lambda argv, **kwargs: Mock(stdout=git_stdout[argv[3]])
        yield m


@pytest.fixture
def docker_module():
    with patch(
        "gbnf_experiment.prepare_filesystem.write_manifest.docker", autospec=True
    ) as m:
        m.image.inspect.return_value.id = IMAGE_ID
        yield m


@pytest.fixture
def filesystem(
    settings,
    prepare_reference_implementation,
    subprocess_module,
    docker_module,
):
    with PreparedFilesystem(
        source_language="javascript",
        include_unit_tests=False,
        include_source_integration_tests=False,
        include_target_integration_tests=False,
        debug=False,
    ) as prepared:
        yield prepared


def manifest(filesystem) -> dict:
    return json.loads((filesystem.run_directory / "manifest.json").read_text())


def describe_the_prompt_the_run_sent():
    def it_is_recorded_beside_the_condition(filesystem):
        """The wording is the treatment, so the run record has to carry it."""
        filesystem.write_manifest(AGENT, prompt=PROMPT, **CONDITION)
        assert manifest(filesystem)["prompt"] == PROMPT

    def it_stays_out_of_the_condition(filesystem):
        filesystem.write_manifest(AGENT, prompt=PROMPT, **CONDITION)
        assert manifest(filesystem)["condition"] == CONDITION


def describe_the_manifest_at_the_start_of_the_run():
    def it_exists_before_the_result_is_written(filesystem):
        filesystem.write_manifest(AGENT, prompt=PROMPT, **CONDITION)
        assert (filesystem.run_directory / "manifest.json").is_file()

    def it_leaves_completed_at_null(filesystem):
        filesystem.write_manifest(AGENT, prompt=PROMPT, **CONDITION)
        assert manifest(filesystem)["completed_at"] is None

    def it_shares_the_run_directory_s_timestamp(filesystem):
        filesystem.write_manifest(AGENT, prompt=PROMPT, **CONDITION)
        assert manifest(filesystem)["timestamp"] == (
            filesystem.timestamp.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        )

    def it_records_the_condition_it_was_given(filesystem):
        filesystem.write_manifest(AGENT, prompt=PROMPT, **CONDITION)
        assert manifest(filesystem)["condition"] == CONDITION


def describe_the_manifest_on_completion():
    def it_stamps_completed_at_in_the_same_iso8601_format(filesystem):
        filesystem.write_manifest(AGENT, prompt=PROMPT, **CONDITION)
        filesystem.write_result('{"is_error": false}', AGENT, prompt=PROMPT, **CONDITION)
        assert re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", manifest(filesystem)["completed_at"]
        )

    def it_stamps_completed_at_no_earlier_than_the_start(filesystem):
        filesystem.write_manifest(AGENT, prompt=PROMPT, **CONDITION)
        filesystem.write_result('{"is_error": false}', AGENT, prompt=PROMPT, **CONDITION)
        recorded = manifest(filesystem)
        assert recorded["completed_at"] >= recorded["timestamp"]

    def it_keeps_the_original_start_timestamp(filesystem):
        filesystem.write_manifest(AGENT, prompt=PROMPT, **CONDITION)
        filesystem.write_result('{"is_error": false}', AGENT, prompt=PROMPT, **CONDITION)
        assert manifest(filesystem)["timestamp"] == (
            filesystem.timestamp.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        )

    def it_carries_no_error_key(filesystem):
        filesystem.write_manifest(AGENT, prompt=PROMPT, **CONDITION)
        filesystem.write_result('{"is_error": false}', AGENT, prompt=PROMPT, **CONDITION)
        assert "error" not in manifest(filesystem)


def describe_the_manifest_on_failure():
    def it_stamps_completed_at(filesystem):
        filesystem.write_manifest(AGENT, prompt=PROMPT, **CONDITION)
        filesystem.write_result(
            None, AGENT, prompt=PROMPT, error="the container died", **CONDITION
        )
        assert re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", manifest(filesystem)["completed_at"]
        )

    def it_marks_the_error(filesystem):
        filesystem.write_manifest(AGENT, prompt=PROMPT, **CONDITION)
        filesystem.write_result(
            None, AGENT, prompt=PROMPT, error="the container died", **CONDITION
        )
        assert manifest(filesystem)["error"] == "the container died"

    def it_keeps_the_error_out_of_the_condition(filesystem):
        filesystem.write_manifest(AGENT, prompt=PROMPT, **CONDITION)
        filesystem.write_result(
            None, AGENT, prompt=PROMPT, error="the container died", **CONDITION
        )
        assert manifest(filesystem)["condition"] == CONDITION

    def it_writes_no_result_json_without_a_result(filesystem):
        filesystem.write_manifest(AGENT, prompt=PROMPT, **CONDITION)
        filesystem.write_result(
            None, AGENT, prompt=PROMPT, error="the container died", **CONDITION
        )
        assert not (filesystem.run_directory / "result.json").exists()

    def it_banks_the_result_when_there_is_one(filesystem):
        filesystem.write_manifest(AGENT, prompt=PROMPT, **CONDITION)
        filesystem.write_result(
            '{"is_error": true}', AGENT, prompt=PROMPT, error="exit 1", **CONDITION
        )
        assert (filesystem.run_directory / "result.json").read_text() == '{"is_error": true}'


def describe_the_reference_the_run_was_handed():
    def it_is_the_folder_the_prepare_image_produced(filesystem, reference):
        assert filesystem.reference_directory == reference

    def it_asks_the_image_for_the_condition_it_was_given(
        filesystem, prepare_reference_implementation
    ):
        asked = prepare_reference_implementation.call_args.kwargs
        assert asked["source_language"] == "javascript"
        assert asked["include_unit_tests"] is False
        assert asked["include_source_integration_tests"] is False
        assert asked["include_target_integration_tests"] is False

    def it_records_what_the_image_put_there(filesystem):
        """The host selects nothing, so the manifest is a read of the folder."""
        filesystem.write_manifest(AGENT, prompt=PROMPT, **CONDITION)
        assert manifest(filesystem)["reference_implementation"]["included"] == [
            "javascript/src/index.ts"
        ]
