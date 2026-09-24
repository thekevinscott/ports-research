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
        m.prepared_directory = tmp_path / "cache" / "prepared"
        m.data_directory = tmp_path / "data"
        yield m


@pytest.fixture
def prepare_cache_key():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.prepare_cache_key",
        "cachekey",
    ):
        yield "cachekey"


@pytest.fixture
def prepare_reference_implementation():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.prepare_reference_implementation",
        autospec=True,
    ) as m:
        yield m


CORPUS = {
    "source/package.json": "{}",
    "source/src/index.js": "export const parse = () => {};\n",
    "tests/python/grammars/arithmetic.gbnf": "root ::= 'x'\n",
}


@pytest.fixture
def assemble_reference_implementation(tmp_path):
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.assemble_reference_implementation",
        autospec=True,
    ) as m:
        corpus = tmp_path / "corpus"
        for name, text in CORPUS.items():
            path = corpus / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        m.return_value = (corpus, [])
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
    prepare_cache_key,
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
    def it_prepares_when_the_keyed_directory_is_absent(
        experiment,
        settings,
        prepare_cache_key,
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
    ):
        experiment()
        prepare_reference_implementation.assert_called_once_with(
            output_directory=settings.prepared_directory / prepare_cache_key,
            debug=False,
        )

    def it_skips_preparing_when_the_keyed_directory_exists(
        experiment,
        settings,
        prepare_cache_key,
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
    ):
        (settings.prepared_directory / prepare_cache_key).mkdir(parents=True)
        experiment()
        prepare_reference_implementation.assert_not_called()

    def it_ports_the_assembled_reference(
        experiment,
        settings,
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
    ):
        experiment()
        assert run_porting_harness.call_args.kwargs["reference_implementation"] is (
            assemble_reference_implementation.return_value[0]
        )
        assert run_porting_harness.call_args.kwargs["output_directory"] == (
            settings.data_directory / RUN_DIRECTORY_NAME / "ported_implementation"
        )

    def it_ports_at_the_configured_effort(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
    ):
        experiment(effort="max")
        assert run_porting_harness.call_args.kwargs["effort"] == "max"

    def it_ports_on_the_configured_model(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
    ):
        experiment(model="claude-sonnet-4-5")
        assert run_porting_harness.call_args.kwargs["model"] == "claude-sonnet-4-5"

    def it_forwards_debug_to_the_preparation_and_the_port(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
    ):
        experiment(debug=True)
        assert prepare_reference_implementation.call_args.kwargs["debug"] is True
        assert run_porting_harness.call_args.kwargs["debug"] is True

    def it_names_the_direction_and_leaves_the_wording_to_the_harness(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
    ):
        experiment(source_language="python")
        assert run_porting_harness.call_args.kwargs["target_language"] == "typescript"
        assert "prompt" not in run_porting_harness.call_args.kwargs

    def it_targets_python_when_porting_from_typescript(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
    ):
        experiment(source_language="typescript")
        assert run_porting_harness.call_args.kwargs["target_language"] == "python"


def describe_the_run_directory():
    def it_lands_directly_in_the_data_directory(
        experiment,
        settings,
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
    ):
        run_directory = experiment()
        assert run_directory == settings.data_directory / RUN_DIRECTORY_NAME

    def it_names_the_directory_from_the_timestamp_alone(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
        run_directory_name,
    ):
        experiment(include_python_tests=True)
        assert run_directory_name.call_args.args[1:] == ()
        assert run_directory_name.call_args.kwargs == {}

    def it_stamps_the_name_with_the_current_utc_time(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
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
        prepare_reference_implementation,
        assemble_reference_implementation,
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
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
    ):
        assert experiment() != experiment()

    def it_captures_the_transcript_beside_the_manifest(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
    ):
        run_directory = experiment()
        assert run_porting_harness.call_args.kwargs["transcripts"] == (
            run_directory / "transcript"
        )

    def it_banks_the_proxy_denial_log_beside_the_manifest(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
    ):
        run_directory = experiment()
        assert run_porting_harness.call_args.kwargs["proxy_log"] == (
            run_directory / "proxy.log"
        )

    def it_creates_the_transcript_directory_before_the_port(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
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
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
        write_manifest,
    ):
        run_directory = experiment()
        assert {call.args for call in write_manifest.call_args_list} == {(run_directory,)}

    def it_records_the_condition_that_ran(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
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
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
        write_manifest,
    ):
        experiment()
        assert write_manifest.call_args.kwargs["gbnf_commit"] is settings.gbnf_commit

    def it_runs_and_records_the_agent_the_caller_chose(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
        write_manifest,
    ):
        """The manifest's image id has to name the harness the port actually ran under."""
        chosen = Mock(name="chosen")

        experiment(agent=chosen)

        assert run_porting_harness.call_args.kwargs["agent"] is chosen
        assert write_manifest.call_args.kwargs["image_tag"] is chosen.image

    def it_shares_the_timestamp_with_the_directory_name(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
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
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
        write_manifest,
    ):
        seen = {}

        def prepare(*args, **kwargs):
            sleep(0.002)
            seen["prepared_at"] = datetime.now(UTC)

        prepare_reference_implementation.side_effect = prepare
        experiment()
        assert write_manifest.call_args.kwargs["timestamp"] < seen["prepared_at"]

    def it_is_written_after_the_port(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
        write_manifest,
    ):
        order = []
        run_porting_harness.side_effect = lambda **kwargs: order.append("port") or DEFAULT
        write_manifest.side_effect = lambda *args, **kwargs: order.append("manifest")
        experiment()
        assert order == ["manifest", "port", "manifest"]


def describe_the_banked_reference():
    def it_assembles_into_a_run_directory_that_already_exists(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
    ):
        seen = {}
        assemble_reference_implementation.side_effect = lambda **kwargs: seen.update(
            existed=kwargs["output_directory"].parent.is_dir()
        ) or (kwargs["output_directory"], [])
        experiment()
        assert seen["existed"] is True

    def it_never_materialises_the_corpus_a_second_time(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
    ):
        run_directory = experiment()
        assert not (run_directory / "reference_implementation").exists()


def describe_the_result():
    def it_banks_the_harness_result_as_result_json(
        experiment,
        prepare_reference_implementation,
        assemble_reference_implementation,
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
        prepare_reference_implementation,
        assemble_reference_implementation,
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
        prepare_reference_implementation,
        assemble_reference_implementation,
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
        prepare_reference_implementation,
        assemble_reference_implementation,
        run_porting_harness,
        write_manifest,
    ):
        run_porting_harness.side_effect = RuntimeError("the container died")
        with pytest.raises(RuntimeError):
            experiment()
        assert write_manifest.call_args.kwargs["error"] == "the container died"
        assert write_manifest.call_args.kwargs["completed_at"] is not None
