from datetime import UTC, datetime
from itertools import count
from time import sleep
from unittest.mock import DEFAULT, Mock, patch

import pytest

from gbnf_experiment.run_gbnf_experiment import run_gbnf_experiment


RUN_DIRECTORY_NAME = "20260906T142530Z_00000000"


@pytest.fixture
def settings(tmp_path):
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.settings", autospec=True
    ) as m:
        m.data_directory = tmp_path / "data"
        yield m


LISTING = [
    "reference_implementation/typescript/package.json",
    "reference_implementation/typescript/src/index.ts",
    "reference_implementation/python/pyproject.toml",
    "tests/python/grammars/arithmetic.gbnf",
]
AGENT_IMAGE = "agent-harness-sandbox-claude:latest"
WORKSPACE_IMAGE = "gbnf-workspace:0123456789abcdef"


@pytest.fixture
def list_prepared_files():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.list_prepared_files",
        autospec=True,
    ) as m:
        m.return_value = list(LISTING)
        yield m


@pytest.fixture
def build_agent_image():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.build_agent_image",
        autospec=True,
    ) as m:
        m.return_value = AGENT_IMAGE
        yield m


@pytest.fixture
def build_workspace_image():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.build_workspace_image",
        autospec=True,
    ) as m:
        m.return_value = WORKSPACE_IMAGE
        yield m


RESULT_JSON = '{"num_turns": 12, "total_cost_usd": 3.21, "is_error": false}'


@pytest.fixture
def run_porting_harness():
    with patch(
        "gbnf_experiment.run_gbnf_experiment.run_porting_harness", autospec=True
    ) as m:
        m.return_value = RESULT_JSON
        yield m


@pytest.fixture
def run_directory_name():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.run_directory_name",
        autospec=True,
    ) as m:
        tokens = count()
        m.side_effect = lambda timestamp: f"20260906T142530Z_{next(tokens):08x}"
        yield m


@pytest.fixture
def write_manifest():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem._write_manifest",
        autospec=True,
    ) as m:
        yield m


AGENT = Mock(name="agent")

CONFIG = {
    "agent": AGENT,
    "source_language": "typescript",
    "include_typescript_tests": False,
    "include_python_tests": False,
    "debug": False,
    "effort": "high",
    "model": "claude-opus-5",
}


@pytest.fixture
def experiment(
    settings,
    list_prepared_files,
    build_agent_image,
    build_workspace_image,
    run_directory_name,
    write_manifest,
):
    def run(**kwargs):
        return run_gbnf_experiment(**{**CONFIG, **kwargs})

    return run


def describe_the_signature():
    @pytest.mark.parametrize(
        "omitted",
        ["agent", "source_language", "include_typescript_tests", "include_python_tests", "debug"],
    )
    def it_requires_every_option(omitted):
        supplied = {name: value for name, value in CONFIG.items() if name != omitted}
        with pytest.raises(TypeError, match=omitted):
            run_gbnf_experiment(**supplied)

    def it_takes_no_positional_argument():
        with pytest.raises(TypeError, match="positional"):
            run_gbnf_experiment("typescript", **CONFIG)


def describe_run():
    def it_ports_inside_the_workspace_image(
        experiment,
        settings,
        run_porting_harness,
    ):
        experiment()
        assert run_porting_harness.call_args.kwargs["image"] == WORKSPACE_IMAGE
        assert run_porting_harness.call_args.kwargs["output_directory"] == (
            settings.data_directory / RUN_DIRECTORY_NAME / "ported_implementation"
        )

    def it_mounts_no_reference_of_its_own(experiment, run_porting_harness):
        experiment()
        assert "reference_implementation" not in run_porting_harness.call_args.kwargs

    def it_bakes_the_selected_files_onto_the_agents_image(
        experiment, build_agent_image, build_workspace_image, run_porting_harness
    ):
        experiment()
        assert build_workspace_image.call_args.kwargs["agent_image"] == AGENT_IMAGE
        assert [p.as_posix() for p in build_workspace_image.call_args.kwargs["files"]] == [
            "reference_implementation/typescript/package.json",
            "reference_implementation/typescript/src/index.ts",
        ]

    def it_ports_at_the_configured_effort(
        experiment,
        run_porting_harness,
    ):
        experiment(effort="max")
        assert run_porting_harness.call_args.kwargs["effort"] == "max"

    def it_ports_on_the_configured_model(
        experiment,
        run_porting_harness,
    ):
        experiment(model="claude-sonnet-4-5")
        assert run_porting_harness.call_args.kwargs["model"] == "claude-sonnet-4-5"

    def it_forwards_debug_to_every_build_and_the_port(
        experiment,
        list_prepared_files,
        build_agent_image,
        build_workspace_image,
        run_porting_harness,
    ):
        experiment(debug=True)
        assert list_prepared_files.call_args.kwargs["debug"] is True
        assert build_agent_image.call_args.kwargs["debug"] is True
        assert build_workspace_image.call_args.kwargs["debug"] is True
        assert run_porting_harness.call_args.kwargs["debug"] is True

    def it_names_the_direction_and_leaves_the_wording_to_the_harness(
        experiment,
        run_porting_harness,
    ):
        experiment(source_language="python")
        assert run_porting_harness.call_args.kwargs["target_language"] == "typescript"
        assert "prompt" not in run_porting_harness.call_args.kwargs

    def it_targets_python_when_porting_from_typescript(
        experiment,
        run_porting_harness,
    ):
        experiment(source_language="typescript")
        assert run_porting_harness.call_args.kwargs["target_language"] == "python"


def describe_the_run_directory():
    def it_lands_directly_in_the_data_directory(
        experiment,
        settings,
        run_porting_harness,
    ):
        run_directory = experiment()
        assert run_directory == settings.data_directory / RUN_DIRECTORY_NAME

    def it_names_the_directory_from_the_timestamp_alone(
        experiment,
        run_porting_harness,
        run_directory_name,
    ):
        experiment(include_python_tests=True)
        assert run_directory_name.call_args.args[1:] == ()
        assert run_directory_name.call_args.kwargs == {}

    def it_stamps_the_name_with_the_current_utc_time(
        experiment,
        run_porting_harness,
        run_directory_name,
    ):
        before = datetime.now(UTC)
        experiment()
        stamped = run_directory_name.call_args.args[0]
        assert stamped.tzinfo is not None
        assert before <= stamped <= datetime.now(UTC)

    def it_exists_before_the_container_starts(
        experiment,
        run_porting_harness,
    ):
        seen = {}
        run_porting_harness.side_effect = lambda **kwargs: seen.update(
            existed=kwargs["output_directory"].is_dir()
        ) or DEFAULT
        experiment()
        assert seen["existed"] is True

    def it_keeps_consecutive_runs_apart(
        experiment,
        settings,
        run_porting_harness,
    ):
        assert experiment() != experiment()

    def it_captures_the_transcript_beside_the_manifest(
        experiment,
        run_porting_harness,
    ):
        run_directory = experiment()
        assert run_porting_harness.call_args.kwargs["transcripts"] == (
            run_directory / "transcript"
        )

    def it_banks_the_proxy_denial_log_beside_the_manifest(
        experiment,
        run_porting_harness,
    ):
        run_directory = experiment()
        assert run_porting_harness.call_args.kwargs["proxy_log"] == (
            run_directory / "proxy.log"
        )

    def it_creates_the_transcript_directory_before_the_port(
        experiment,
        run_porting_harness,
    ):
        seen = {}
        run_porting_harness.side_effect = lambda **kwargs: seen.update(
            existed=kwargs["transcripts"].is_dir()
        ) or DEFAULT
        experiment()
        assert seen["existed"] is True


def describe_the_manifest():
    def it_is_written_into_the_run_directory(
        experiment,
        run_porting_harness,
        write_manifest,
    ):
        run_directory = experiment()
        assert {call.args for call in write_manifest.call_args_list} == {(run_directory,)}

    def it_records_the_condition_that_ran(
        experiment,
        run_porting_harness,
        write_manifest,
    ):
        experiment(
            source_language="python",
            include_typescript_tests=True,
            effort="low",
            model="claude-sonnet-4-5",
        )
        assert write_manifest.call_args.kwargs["condition"] == {
            "name": "source-python_typescript-tests_effort-low_model-claude-sonnet-4-5",
            "source_language": "python",
            "target_language": "typescript",
            "include_typescript_tests": True,
            "include_python_tests": False,
            "effort": "low",
            "model": "claude-sonnet-4-5",
        }

    def it_records_the_pinned_commit(
        experiment,
        settings,
        run_porting_harness,
        write_manifest,
    ):
        experiment()
        assert write_manifest.call_args.kwargs["gbnf_commit"] is settings.gbnf_commit

    def it_runs_and_records_the_agent_the_caller_chose(
        experiment,
        build_agent_image,
        run_porting_harness,
        write_manifest,
    ):
        """The manifest's image id has to name the workspace the port actually ran in."""
        chosen = Mock(name="chosen")

        experiment(agent=chosen)

        assert build_agent_image.call_args.kwargs["agent"] is chosen
        assert run_porting_harness.call_args.kwargs["agent"] is chosen
        assert write_manifest.call_args.kwargs["image"] == WORKSPACE_IMAGE

    def it_shares_the_timestamp_with_the_directory_name(
        experiment,
        run_porting_harness,
        run_directory_name,
        write_manifest,
    ):
        experiment()
        assert write_manifest.call_args.kwargs["timestamp"] is (
            run_directory_name.call_args.args[0]
        )

    def it_stamps_the_run_from_before_the_preparation(
        experiment,
        list_prepared_files,
        run_porting_harness,
        write_manifest,
    ):
        seen = {}

        def prepare(*args, **kwargs):
            sleep(0.002)
            seen["prepared_at"] = datetime.now(UTC)
            return list(LISTING)

        list_prepared_files.side_effect = prepare
        experiment()
        assert write_manifest.call_args.kwargs["timestamp"] < seen["prepared_at"]

    def it_is_written_after_the_port(
        experiment,
        run_porting_harness,
        write_manifest,
    ):
        order = []
        run_porting_harness.side_effect = lambda **kwargs: order.append("port") or DEFAULT
        write_manifest.side_effect = lambda *args, **kwargs: order.append("manifest")
        experiment()
        assert order == ["manifest", "port", "manifest"]


def describe_the_banked_reference():
    def it_never_materialises_the_corpus_on_the_host(
        experiment,
        run_porting_harness,
    ):
        run_directory = experiment()
        assert not (run_directory / "reference_implementation").exists()


def describe_the_result():
    def it_banks_the_harness_result_as_result_json(
        experiment,
        run_porting_harness,
    ):
        run_porting_harness.return_value = RESULT_JSON
        run_directory = experiment()
        result = run_directory / "result.json"
        assert result.is_file()
        assert result.read_text() == RESULT_JSON

    def it_writes_no_result_when_the_port_dies(
        experiment,
        settings,
        run_porting_harness,
    ):
        run_porting_harness.side_effect = RuntimeError("the container died")
        with pytest.raises(RuntimeError):
            experiment()
        run_directory = settings.data_directory / RUN_DIRECTORY_NAME
        assert not (run_directory / "result.json").exists()

    def it_banks_what_a_dead_port_printed(
        experiment,
        settings,
        run_porting_harness,
    ):
        died = RuntimeError("exited 1")
        died.stdout = RESULT_JSON
        run_porting_harness.side_effect = died
        with pytest.raises(RuntimeError):
            experiment()
        run_directory = settings.data_directory / RUN_DIRECTORY_NAME
        assert (run_directory / "result.json").read_text() == RESULT_JSON

    def it_completes_the_manifest_with_the_error_when_the_port_dies(
        experiment,
        run_porting_harness,
        write_manifest,
    ):
        run_porting_harness.side_effect = RuntimeError("the container died")
        with pytest.raises(RuntimeError):
            experiment()
        assert write_manifest.call_args.kwargs["error"] == "the container died"
        assert write_manifest.call_args.kwargs["completed_at"] is not None
