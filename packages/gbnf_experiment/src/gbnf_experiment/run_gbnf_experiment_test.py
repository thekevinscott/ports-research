from datetime import UTC, datetime
from pathlib import Path
from time import sleep
from unittest.mock import DEFAULT, Mock, patch

import pytest

from botbox import RunResult
from prompt import Prompt

from gbnf_experiment.run_gbnf_experiment import PROMPT_PATH, AgentFailed, run_gbnf_experiment


@pytest.fixture
def config(tmp_path):
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.config", autospec=True
    ) as m:
        m.PREPARED_DIRECTORY = tmp_path / "cache" / "prepared"
        yield m


@pytest.fixture
def run_directory(tmp_path):
    directory = tmp_path / "data" / "runs" / "models-effort" / "brave-otter"
    directory.mkdir(parents=True)
    return directory


SHARED = {
    "javascript/package.json": "{}",
    "javascript/src/index.ts": "export const parse = () => {};\n",
}


@pytest.fixture
def prepare_reference_implementation(config):
    """Returns the extracted /shared, a cache entry in upstream layout."""
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.prepare_reference_implementation",
        autospec=True,
    ) as m:
        shared = config.PREPARED_DIRECTORY / "key"
        for name, text in SHARED.items():
            path = shared / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        m.return_value = shared
        yield m


RESULT_JSON = '{"num_turns": 12, "is_error": false}'
TRANSCRIPT = {
    ".claude/projects/-target/session.jsonl": '{"type": "user"}\n',
    ".claude/projects/-target/session/subagents/agent-1.jsonl": '{"type": "assistant"}\n',
}
PROXY_LOG = "CONNECT api.anthropic.com:443\n"
RUN_RESULT = RunResult(
    stdout=RESULT_JSON, stderr="", exit_code=0, transcript=TRANSCRIPT, proxy=PROXY_LOG, container="container", image="image"
)


@pytest.fixture
def port_codebase():
    with patch(
        "gbnf_experiment.run_gbnf_experiment.port_codebase", autospec=True
    ) as m:
        m.return_value = RUN_RESULT
        yield m


@pytest.fixture
def write_manifest():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem._write_manifest",
        autospec=True,
    ) as m:
        yield m


AGENT = Mock(name="agent", model="claude-opus-5", effort="high")

CONFIG = {
    "agent": AGENT,
    "run_directory": Path("/experiments/v2-models-effort/runs/brave-otter"),
    "source_language": "javascript",
    "include_unit_tests": False,
    "include_source_integration_tests": False,
    "include_target_integration_tests": False,
    "debug": False,
}


@pytest.fixture
def experiment(
    config,
    prepare_reference_implementation,
    write_manifest,
    run_directory,
):
    def run(**kwargs):
        return run_gbnf_experiment(**{**CONFIG, "run_directory": run_directory, **kwargs})

    return run


def describe_the_signature():
    @pytest.mark.parametrize(
        "omitted",
        [
            "agent",
            "run_directory",
            "source_language",
            "include_unit_tests",
            "include_source_integration_tests",
            "include_target_integration_tests",
            "debug",
        ],
    )
    def it_requires_every_option(omitted):
        supplied = {name: value for name, value in CONFIG.items() if name != omitted}
        with pytest.raises(TypeError, match=omitted):
            run_gbnf_experiment(**supplied)

    def it_takes_no_positional_argument():
        with pytest.raises(TypeError, match="positional"):
            run_gbnf_experiment("javascript", **CONFIG)


def describe_run():
    def it_prepares_the_condition(experiment, prepare_reference_implementation, port_codebase):
        experiment(source_language="python", include_unit_tests=True)
        prepare_reference_implementation.assert_called_once_with(
            source_language="python",
            include_unit_tests=True,
            include_source_integration_tests=False,
            include_target_integration_tests=False,
            debug=False,
        )

    def it_ports_the_prepared_reference(
        experiment,
        run_directory,
        prepare_reference_implementation,
        port_codebase,
    ):
        experiment()
        assert port_codebase.call_args.kwargs["source"] is (
            prepare_reference_implementation.return_value
        )
        assert port_codebase.call_args.kwargs["output"] == run_directory / "ported_implementation"

    def it_ports_with_the_agent_the_caller_chose(
        experiment,
        prepare_reference_implementation,
        port_codebase,
    ):
        chosen = Mock(name="chosen", model="claude-sonnet-4-5", effort="max")
        experiment(agent=chosen)
        assert port_codebase.call_args.kwargs["agent"] is chosen

    def it_forwards_debug_to_the_preparation_only(
        experiment,
        prepare_reference_implementation,
        port_codebase,
    ):
        experiment(debug=True)
        assert prepare_reference_implementation.call_args.kwargs["debug"] is True
        assert "debug" not in port_codebase.call_args.kwargs

    def it_names_the_direction_in_the_prompt_it_sends(
        experiment,
        prepare_reference_implementation,
        port_codebase,
    ):
        experiment(source_language="python")
        assert port_codebase.call_args.kwargs["prompt"] == (
            str(
                Prompt(
                    PROMPT_PATH,
                    source_language="python",
                    target_language="typescript",
                    suites_information="",
                )
            )
        )

    def it_targets_python_when_porting_from_javascript(
        experiment,
        prepare_reference_implementation,
        port_codebase,
    ):
        experiment(source_language="javascript")
        assert port_codebase.call_args.kwargs["prompt"] == (
            str(
                Prompt(
                    PROMPT_PATH,
                    source_language="javascript",
                    target_language="python",
                    suites_information="",
                )
            )
        )

    def it_names_the_suites_the_condition_mounted(
        experiment,
        prepare_reference_implementation,
        port_codebase,
    ):
        experiment(include_target_integration_tests=True)
        assert "python/tests/generated/" in port_codebase.call_args.kwargs["prompt"]

    def it_names_no_suite_when_the_condition_mounted_none(
        experiment,
        prepare_reference_implementation,
        port_codebase,
    ):
        experiment()
        assert "tests" not in port_codebase.call_args.kwargs["prompt"]

    def it_leaves_no_placeholder_in_the_prompt(
        experiment,
        prepare_reference_implementation,
        port_codebase,
    ):
        experiment()
        prompt = port_codebase.call_args.kwargs["prompt"]
        assert "{" not in prompt
        assert "}" not in prompt


def describe_the_run_directory():
    def it_writes_into_the_folder_it_was_given(
        experiment,
        run_directory,
        prepare_reference_implementation,
        port_codebase,
    ):
        experiment()
        assert sorted(path.name for path in run_directory.iterdir()) == [
            "ported_implementation",
            "proxy.log",
            "result.json",
            "stderr.txt",
            "transcript",
        ]

    def it_creates_no_folder_of_its_own(
        experiment,
        run_directory,
        prepare_reference_implementation,
        port_codebase,
    ):
        experiment()
        assert list(run_directory.parent.iterdir()) == [run_directory]

    def it_returns_nothing(
        experiment,
        prepare_reference_implementation,
        port_codebase,
    ):
        assert experiment() is None

    def it_exists_before_the_container_starts(
        experiment,
        prepare_reference_implementation,
        port_codebase,
    ):
        seen = {}
        port_codebase.side_effect = lambda **kwargs: seen.update(
            existed=kwargs["output"].is_dir()
        ) or DEFAULT
        experiment()
        assert seen["existed"] is True

    def it_banks_each_transcript_file_at_its_path_under_transcript(
        experiment,
        prepare_reference_implementation,
        port_codebase,
        run_directory,
    ):
        experiment()
        banked = {
            path.relative_to(run_directory / "transcript").as_posix(): path.read_text()
            for path in (run_directory / "transcript").rglob("*")
            if path.is_file()
        }
        assert banked == TRANSCRIPT

    def it_banks_the_proxy_log_beside_the_manifest(
        experiment,
        prepare_reference_implementation,
        port_codebase,
        run_directory,
    ):
        experiment()
        assert (run_directory / "proxy.log").read_text() == PROXY_LOG


def describe_the_manifest():
    def it_is_written_into_the_run_directory(
        experiment,
        prepare_reference_implementation,
        port_codebase,
        write_manifest,
        run_directory,
    ):
        experiment()
        assert {call.args for call in write_manifest.call_args_list} == {(run_directory,)}

    def it_records_no_study(
        experiment,
        prepare_reference_implementation,
        port_codebase,
        write_manifest,
    ):
        experiment()
        assert ["study" in call.kwargs for call in write_manifest.call_args_list] == [False, False]

    def it_records_the_condition_that_ran(
        experiment,
        prepare_reference_implementation,
        port_codebase,
        write_manifest,
    ):
        experiment(
            agent=Mock(name="agent", model="claude-sonnet-4-5", effort="low"),
            source_language="python",
            include_source_integration_tests=True,
        )
        assert write_manifest.call_args.kwargs["condition"] == {
            "name": "source-python_source-integration-tests_effort-low_model-claude-sonnet-4-5",
            "source_language": "python",
            "target_language": "javascript",
            "include_unit_tests": False,
            "include_source_integration_tests": True,
            "include_target_integration_tests": False,
            "effort": "low",
            "model": "claude-sonnet-4-5",
        }

    def it_records_the_pinned_commit(
        experiment,
        config,
        prepare_reference_implementation,
        port_codebase,
        write_manifest,
    ):
        experiment()
        assert write_manifest.call_args.kwargs["gbnf_commit"] is config.GBNF_COMMIT

    def it_runs_and_records_the_agent_the_caller_chose(
        experiment,
        prepare_reference_implementation,
        port_codebase,
        write_manifest,
    ):
        """The manifest's image id has to name the harness the port actually ran under."""
        chosen = Mock(name="chosen", model="claude-sonnet-4-5", effort="max")

        experiment(agent=chosen)

        assert port_codebase.call_args.kwargs["agent"] is chosen
        assert write_manifest.call_args.kwargs["image_tag"] is chosen.image

    def it_stamps_the_run_from_before_the_preparation(
        experiment,
        prepare_reference_implementation,
        port_codebase,
        write_manifest,
    ):
        seen = {}

        def prepare(*args, **kwargs):
            sleep(0.002)
            seen["prepared_at"] = datetime.now(UTC)
            return DEFAULT

        prepare_reference_implementation.side_effect = prepare
        experiment()
        assert write_manifest.call_args.kwargs["timestamp"] < seen["prepared_at"]

    def it_is_written_after_the_port(
        experiment,
        prepare_reference_implementation,
        port_codebase,
        write_manifest,
    ):
        order = []
        port_codebase.side_effect = lambda **kwargs: order.append("port") or DEFAULT
        write_manifest.side_effect = lambda *args, **kwargs: order.append("manifest")
        experiment()
        assert order == ["manifest", "port", "manifest"]


def describe_the_banked_reference():
    def it_records_what_the_agent_was_shown(
        experiment,
        prepare_reference_implementation,
        port_codebase,
        write_manifest,
    ):
        experiment()
        assert write_manifest.call_args.kwargs["included"] == sorted(SHARED)

    def it_never_materialises_the_corpus_a_second_time(
        experiment,
        prepare_reference_implementation,
        port_codebase,
        run_directory,
    ):
        experiment()
        assert not (run_directory / "reference_implementation").exists()


def describe_the_result():
    def it_banks_the_agent_stdout_as_result_json(
        experiment,
        prepare_reference_implementation,
        port_codebase,
        run_directory,
    ):
        experiment()
        result = run_directory / "result.json"
        assert result.is_file()
        assert result.read_text() == RESULT_JSON

    def it_writes_no_result_when_the_port_dies(
        experiment,
        run_directory,
        prepare_reference_implementation,
        port_codebase,
    ):
        port_codebase.side_effect = RuntimeError("the container died")
        with pytest.raises(RuntimeError):
            experiment()
        assert not (run_directory / "result.json").exists()

    def it_banks_the_stdout_of_a_non_zero_exit(
        experiment,
        prepare_reference_implementation,
        port_codebase,
        run_directory,
    ):
        port_codebase.return_value = RunResult(
            stdout=RESULT_JSON, stderr="", exit_code=1, transcript={}, proxy="", container="container", image="image"
        )
        with pytest.raises(AgentFailed):
            experiment()
        assert (run_directory / "result.json").read_text() == RESULT_JSON

    def it_propagates_the_port_s_exception_unchanged(
        experiment,
        prepare_reference_implementation,
        port_codebase,
    ):
        died = RuntimeError("the container died")
        port_codebase.side_effect = died
        with pytest.raises(RuntimeError) as raised:
            experiment()
        assert raised.value is died

    def it_completes_the_manifest_with_the_error_when_the_port_dies(
        experiment,
        prepare_reference_implementation,
        port_codebase,
        write_manifest,
    ):
        port_codebase.side_effect = RuntimeError("the container died")
        with pytest.raises(RuntimeError):
            experiment()
        assert write_manifest.call_args.kwargs["error"] == "the container died"
        assert write_manifest.call_args.kwargs["completed_at"] is not None

    def it_records_the_agent_s_exit_code_in_the_manifest(
        experiment,
        prepare_reference_implementation,
        port_codebase,
        write_manifest,
    ):
        port_codebase.return_value = RunResult(
            stdout=RESULT_JSON, stderr="", exit_code=1, transcript={}, proxy="", container="container", image="image"
        )
        with pytest.raises(AgentFailed):
            experiment()
        assert write_manifest.call_args.kwargs["exit_code"] == 1

    def it_banks_the_agent_s_stderr_beside_the_result(
        experiment,
        prepare_reference_implementation,
        port_codebase,
        run_directory,
    ):
        port_codebase.return_value = RunResult(
            stdout=RESULT_JSON, stderr="Error: rate limited\n", exit_code=1, transcript={}, proxy="", container="container", image="image"
        )
        with pytest.raises(AgentFailed):
            experiment()
        assert (run_directory / "stderr.txt").read_text() == "Error: rate limited\n"


ERROR_RESULT_JSON = (
    '{"type": "result", "subtype": "success", "is_error": true,'
    ' "api_error_status": 429, "result": "API Error: 429 rate limited"}'
)


def describe_a_failed_agent():
    @pytest.fixture
    def failed(port_codebase):
        port_codebase.return_value = RunResult(
            stdout=ERROR_RESULT_JSON, stderr="", exit_code=0, transcript=TRANSCRIPT, proxy=PROXY_LOG, container="container", image="image"
        )

    def it_raises_with_the_agent_s_error_text(experiment, failed):
        with pytest.raises(AgentFailed, match="API Error: 429 rate limited"):
            experiment()

    def it_raises_when_the_agent_exits_non_zero(experiment, port_codebase):
        port_codebase.return_value = RunResult(
            stdout=RESULT_JSON, stderr="", exit_code=137, transcript={}, proxy="", container="container", image="image"
        )
        with pytest.raises(AgentFailed):
            experiment()

    def it_banks_every_artifact_before_raising(experiment, failed, run_directory):
        with pytest.raises(AgentFailed):
            experiment()
        assert (run_directory / "result.json").read_text() == ERROR_RESULT_JSON
        assert (run_directory / "proxy.log").read_text() == PROXY_LOG
        assert {
            path.relative_to(run_directory / "transcript").as_posix()
            for path in (run_directory / "transcript").rglob("*")
            if path.is_file()
        } == set(TRANSCRIPT)

    def it_records_the_error_text_in_the_manifest(experiment, failed, write_manifest):
        with pytest.raises(AgentFailed):
            experiment()
        assert write_manifest.call_args.kwargs["error"] == "API Error: 429 rate limited"
        assert write_manifest.call_args.kwargs["completed_at"] is not None
