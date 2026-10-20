import json
import re
from datetime import UTC
from unittest.mock import Mock, patch

import pytest

from botbox import RunResult

from gbnf_experiment.prepare_filesystem import PreparedFilesystem

HEAD = "c" * 40
IMAGE_ID = "sha256:" + "b" * 64

AGENT = Mock(name="agent")
AGENT.image = "botbox-claude:latest"

TESTS = {
    "include_unit_tests": False,
    "include_source_integration_tests": False,
    "include_target_integration_tests": True,
}
CONDITION = {
    "source_language": "javascript",
    **TESTS,
    "effort": "high",
    "model": "claude-opus-5",
}
SHARED = (
    "javascript/package.json",
    "javascript/src/gbnf.ts",
    "python/tests/generated/iteration/iteration_test.py",
)


def run_result(stdout='{"is_error": false}', stderr="", exit_code=0) -> RunResult:
    return RunResult(stdout=stdout, stderr=stderr, exit_code=exit_code, transcript={}, proxy="", container="container", image="image")


@pytest.fixture
def config(tmp_path):
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.config", autospec=True
    ) as m:
        m.PREPARED_DIRECTORY = tmp_path / "cache" / "prepared"
        m.GBNF_COMMIT = "13f1aca"
        yield m


@pytest.fixture
def prepare_reference_implementation(tmp_path):
    """Returns the extracted /shared: a cache entry in upstream layout."""
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.prepare_reference_implementation",
        autospec=True,
    ) as m:
        shared = tmp_path / "cache" / "prepared" / "key"
        for name in SHARED:
            (shared / name).parent.mkdir(parents=True, exist_ok=True)
            (shared / name).write_text(name)
        m.return_value = shared
        yield m


@pytest.fixture
def git_stdout():
    return {"rev-parse": HEAD + "\n", "status": ""}


@pytest.fixture
def subprocess_module(config, git_stdout):
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
def run_directory(tmp_path):
    directory = tmp_path / "data" / "runs" / "tests-configuration" / "brave-otter"
    directory.mkdir(parents=True)
    return directory


@pytest.fixture
def filesystem(
    config,
    prepare_reference_implementation,
    subprocess_module,
    docker_module,
    run_directory,
):
    return PreparedFilesystem(source_language="javascript", **TESTS, debug=False, run_directory=run_directory)


def manifest(filesystem) -> dict:
    return json.loads((filesystem.run_directory / "manifest.json").read_text())


def complete(filesystem, result: RunResult) -> None:
    with filesystem.recording(AGENT, **CONDITION) as run:
        run.result = result


def fail(filesystem, error: str, result: RunResult | None = None) -> None:
    with pytest.raises(RuntimeError, match=error):
        with filesystem.recording(AGENT, **CONDITION) as run:
            run.result = result
            raise RuntimeError(error)


def describe_the_reference_implementation():
    def it_prepares_the_condition(filesystem, prepare_reference_implementation):
        prepare_reference_implementation.assert_called_once_with(
            source_language="javascript", **TESTS, debug=False
        )

    def it_is_the_extracted_shared_tree_unchanged(filesystem, prepare_reference_implementation):
        assert filesystem.reference_implementation_directory is (
            prepare_reference_implementation.return_value
        )

    def it_lists_every_file_in_it_relative_to_its_root(filesystem):
        with filesystem.recording(AGENT, **CONDITION):
            assert manifest(filesystem)["reference_implementation"]["included"] == list(SHARED)


def describe_the_run_directory():
    def it_is_the_folder_it_was_given(filesystem, run_directory):
        assert filesystem.run_directory == run_directory

    def it_lays_the_run_out_inside_it(filesystem, run_directory):
        assert sorted(path.name for path in run_directory.iterdir()) == ["ported_implementation", "transcript"]

    def it_requires_a_run_directory(config, prepare_reference_implementation):
        with pytest.raises(TypeError, match="run_directory"):
            PreparedFilesystem(source_language="javascript", **TESTS, debug=False)


def describe_the_manifest_at_the_start_of_the_run():
    def it_exists_once_recording_starts(filesystem):
        with filesystem.recording(AGENT, **CONDITION):
            assert (filesystem.run_directory / "manifest.json").is_file()

    def it_leaves_completed_at_null(filesystem):
        with filesystem.recording(AGENT, **CONDITION):
            assert manifest(filesystem)["completed_at"] is None

    def it_shares_the_run_directory_s_timestamp(filesystem):
        with filesystem.recording(AGENT, **CONDITION):
            assert manifest(filesystem)["timestamp"] == (
                filesystem.timestamp.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            )

    def it_records_the_condition_it_was_given(filesystem):
        with filesystem.recording(AGENT, **CONDITION):
            assert manifest(filesystem)["condition"] == CONDITION

    def it_records_no_study(filesystem):
        with filesystem.recording(AGENT, **CONDITION):
            assert "study" not in manifest(filesystem)


def describe_the_manifest_on_completion():
    def it_stamps_completed_at_in_the_same_iso8601_format(filesystem):
        complete(filesystem, run_result())
        assert re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", manifest(filesystem)["completed_at"]
        )

    def it_stamps_completed_at_no_earlier_than_the_start(filesystem):
        complete(filesystem, run_result())
        recorded = manifest(filesystem)
        assert recorded["completed_at"] >= recorded["timestamp"]

    def it_keeps_the_original_start_timestamp(filesystem):
        complete(filesystem, run_result())
        assert manifest(filesystem)["timestamp"] == (
            filesystem.timestamp.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        )

    def it_carries_no_error_key(filesystem):
        complete(filesystem, run_result())
        assert "error" not in manifest(filesystem)

    def it_keeps_the_condition_on_completion(filesystem):
        complete(filesystem, run_result())
        assert manifest(filesystem)["condition"] == CONDITION

    def it_records_the_agent_s_exit_code(filesystem):
        complete(filesystem, run_result(exit_code=3))
        assert manifest(filesystem)["exit_code"] == 3

    def it_banks_the_agent_s_stdout_as_result_json(filesystem):
        complete(filesystem, run_result(stdout='{"num_turns": 4}'))
        assert (filesystem.run_directory / "result.json").read_text() == '{"num_turns": 4}'

    def it_banks_the_agent_s_stderr_beside_the_result(filesystem):
        complete(filesystem, run_result(stderr="warning: x\n"))
        assert (filesystem.run_directory / "stderr.txt").read_text() == "warning: x\n"

    def it_banks_an_empty_stderr_as_an_empty_file(filesystem):
        complete(filesystem, run_result(stderr=""))
        assert (filesystem.run_directory / "stderr.txt").read_text() == ""


def describe_the_manifest_on_failure():
    def it_lets_the_exception_propagate_unchanged(filesystem):
        died = RuntimeError("the container died")
        with pytest.raises(RuntimeError) as raised:
            with filesystem.recording(AGENT, **CONDITION):
                raise died
        assert raised.value is died

    def it_stamps_completed_at(filesystem):
        fail(filesystem, "the container died")
        assert re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", manifest(filesystem)["completed_at"]
        )

    def it_marks_the_error(filesystem):
        fail(filesystem, "the container died")
        assert manifest(filesystem)["error"] == "the container died"

    def it_keeps_the_error_out_of_the_condition(filesystem):
        fail(filesystem, "the container died")
        assert manifest(filesystem)["condition"] == CONDITION

    def it_writes_no_result_json_without_a_result(filesystem):
        fail(filesystem, "the container died")
        assert not (filesystem.run_directory / "result.json").exists()

    def it_writes_no_stderr_without_a_result(filesystem):
        fail(filesystem, "the container died")
        assert not (filesystem.run_directory / "stderr.txt").exists()

    def it_records_no_exit_code_without_a_result(filesystem):
        fail(filesystem, "the container died")
        assert "exit_code" not in manifest(filesystem)

    def it_banks_the_result_alongside_the_error(filesystem):
        fail(filesystem, "API Error: 429", run_result(stdout='{"is_error": true}', exit_code=1))
        assert (filesystem.run_directory / "result.json").read_text() == '{"is_error": true}'
        assert manifest(filesystem)["exit_code"] == 1
        assert manifest(filesystem)["error"] == "API Error: 429"
