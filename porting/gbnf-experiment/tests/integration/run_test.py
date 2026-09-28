"""The pipeline end to end with the model faked and the prepare image real.

The prepare image is the only thing not stood in for: nothing it does is
billed and no model is involved, and what it leaves at /shared is the
experiment. Kevin: "This is really the whole shebang and what screwed the v1
of the experiment, so it's important to get it right in the lowest cost way
we can" and "I think it _should_ be asserted through docker, no? Otherwise
it's testing theater?"
"""

import json
import re
from itertools import product
from pathlib import Path

import pytest
from click.testing import CliRunner
from python_on_whales.exceptions import DockerException

from agent_harness_sandbox.agents.ClaudeAgent import ClaudeAgent
from gbnf_experiment import run_gbnf_experiment
from gbnf_experiment.cli import cli
from gbnf_experiment.config import settings
from gbnf_experiment.render_prompt import render_prompt

FIXTURES = Path(__file__).parent / "fixtures" / "shared"
CONDITIONS = list(
    product(("javascript", "python"), (False, True), (False, True), (False, True))
)

CONFIG = {
    "source_language": "javascript",
    "include_unit_tests": False,
    "include_source_integration_tests": False,
    "include_target_integration_tests": False,
    "debug": False,
    "effort": "high",
    "model": "claude-opus-5",
}


def fixture_name(source_language, unit, source_integration, target_integration) -> str:
    """The condition as the fixtures name it."""
    return (
        f"{source_language}_unit-{unit}"
        f"_source-integration-{source_integration}"
        f"_target-integration-{target_integration}"
    ).lower()


def assembled(name) -> list[str]:
    return [f"/input/{line}" for line in (FIXTURES / f"{name}.txt").read_text().splitlines()]


@pytest.fixture
def experiment(data_directory, porting_docker, claude_home):
    def run(**kwargs):
        agent = ClaudeAgent(host_home=claude_home)
        return run_gbnf_experiment(**{"agent": agent, **CONFIG, **kwargs})

    return run


def describe_gbnf_experiment():
    def describe_the_assembled_reference():
        @pytest.mark.parametrize(
            ("source_language", "unit", "source_integration", "target_integration"),
            CONDITIONS,
            ids=[fixture_name(*condition) for condition in CONDITIONS],
        )
        def it_gives_the_container_the_tree_the_image_assembled(
            experiment,
            porting_calls,
            source_language,
            unit,
            source_integration,
            target_integration,
        ):
            """One mount, the upstream layout, exactly the whitelisted files."""
            experiment(
                source_language=source_language,
                include_unit_tests=unit,
                include_source_integration_tests=source_integration,
                include_target_integration_tests=target_integration,
            )
            [call] = porting_calls
            assert [
                path for path in call["container_tree"] if path.startswith("/input/")
            ] == assembled(
                fixture_name(source_language, unit, source_integration, target_integration)
            )

        def it_stages_the_assembly_outside_the_run_record(experiment, data_directory):
            """The corpus is rebuildable from the image, so no run banks a copy."""
            experiment()
            experiment(include_unit_tests=True)
            assert all(
                not (run / "reference_implementation").exists()
                for run in data_directory.iterdir()
            )

        def it_stages_no_input_tree_beside_the_runs(experiment, data_directory):
            """data/ is a flat list of run directories and holds nothing else."""
            experiment()
            experiment(include_unit_tests=True)
            assert all(
                re.fullmatch(r"\d{8}T\d{6}Z_[0-9a-f]{8}", path.name) and path.is_dir()
                for path in data_directory.iterdir()
            )

        def it_throws_the_staged_corpus_away_when_the_run_ends(
            experiment, porting_calls, data_directory
        ):
            experiment()
            [call] = porting_calls
            [staged] = [
                Path(source)
                for source, target, _ in call["volumes"]
                if str(target) == "/input"
            ]
            assert data_directory not in staged.parents
            assert not staged.exists()

    def describe_the_port():
        def it_sends_the_prompt_this_package_renders(experiment, porting_calls):
            experiment(source_language="javascript")
            [call] = porting_calls
            assert call["prompt"] == render_prompt(
                source_language="javascript", target_language="python"
            )

        def it_renders_the_reverse_direction(experiment, porting_calls):
            experiment(source_language="python")
            [call] = porting_calls
            assert call["prompt"] == render_prompt(
                source_language="python", target_language="javascript"
            )

        def it_collects_the_port_into_the_run_directory(experiment, data_directory):
            experiment()
            [run_directory] = data_directory.iterdir()
            assert (run_directory / "ported_implementation" / "ported.py").is_file()

        def it_pins_the_model_in_the_argv_the_container_runs(experiment, porting_calls):
            experiment(model="claude-sonnet-4-5")
            [call] = porting_calls
            command = call["command"]
            assert command[command.index("--model") + 1] == "claude-sonnet-4-5"


def describe_the_run_directory():
    def it_creates_one_directory_per_run(experiment, data_directory):
        experiment()
        [run_directory] = data_directory.iterdir()
        assert (run_directory / "ported_implementation").is_dir()

    def it_stamps_the_name_with_utc_and_a_random_token(experiment, data_directory):
        experiment(include_unit_tests=True)
        [run_directory] = data_directory.iterdir()
        assert re.fullmatch(r"\d{8}T\d{6}Z_[0-9a-f]{8}", run_directory.name)

    def it_keeps_consecutive_runs_apart(experiment):
        assert experiment() != experiment()

    def it_gives_two_conditions_two_directories(experiment, data_directory):
        experiment(source_language="javascript")
        experiment(source_language="python")
        assert len(list(data_directory.iterdir())) == 2

    def it_exists_before_the_container_starts(experiment, porting_docker):
        experiment()
        porting_docker.run.assert_called_once()

    def it_banks_the_proxy_log_the_jail_wrote(experiment, data_directory):
        experiment()
        [run_directory] = data_directory.iterdir()
        assert (run_directory / "proxy.log").is_file()

    def it_banks_a_transcript_directory_beside_the_manifest(experiment, data_directory):
        experiment()
        [run_directory] = data_directory.iterdir()
        assert (run_directory / "transcript").is_dir()


def describe_the_clean_slate():
    def it_starts_the_container_with_an_empty_output_directory(experiment, porting_calls):
        experiment()
        [call] = porting_calls
        assert not any(
            path.startswith("/workspace/ported_implementation")
            for path in call["container_tree"]
        )

    def it_hides_one_run_s_output_from_the_next(
        experiment, porting_calls, data_directory
    ):
        experiment()
        experiment()
        ports = list(data_directory.glob("*/ported_implementation/ported.py"))
        assert len(ports) == 2
        _, second = porting_calls
        assert not any(
            path.startswith("/workspace/ported_implementation")
            for path in second["container_tree"]
        )


def describe_the_manifest():
    def it_lands_in_the_run_directory(experiment, manifest):
        experiment()
        assert set(manifest()) == {
            "timestamp",
            "completed_at",
            "prompt",
            "condition",
            "derivation",
            "reference_implementation",
            "sandbox",
            "harness",
        }

    def it_records_the_condition_that_ran(experiment, manifest):
        experiment(
            source_language="python",
            include_unit_tests=True,
            effort="low",
            model="claude-sonnet-4-5",
        )
        assert manifest()["condition"] == {
            "name": "source-python_unit-tests_effort-low_model-claude-sonnet-4-5",
            "source_language": "python",
            "target_language": "javascript",
            "include_unit_tests": True,
            "include_source_integration_tests": False,
            "include_target_integration_tests": False,
            "effort": "low",
            "model": "claude-sonnet-4-5",
        }

    def it_records_the_prompt_sent(experiment, manifest, porting_calls):
        experiment()
        [call] = porting_calls
        assert manifest()["prompt"] == call["prompt"]

    def it_records_the_paths_the_image_put_in_the_reference(experiment, manifest):
        """The host selects nothing, so the manifest is a read of the folder."""
        experiment(source_language="python", include_unit_tests=True)
        assert manifest()["reference_implementation"]["included"] == [
            path.removeprefix("/input/")
            for path in assembled(fixture_name("python", True, False, False))
        ]

    def it_records_the_pinned_commit(experiment, manifest):
        experiment()
        assert manifest()["derivation"] == {"gbnf_commit": settings.gbnf_commit}

    def it_identifies_the_sandbox_by_image_id_alone(experiment, manifest, sandbox_image_id):
        """The tag is a constant, so only the id says which image ran."""
        experiment()
        assert manifest()["sandbox"] == {"image_id": sandbox_image_id}

    def it_records_one_commit_for_the_whole_harness(experiment, manifest):
        experiment()
        harness = manifest()["harness"]
        assert re.fullmatch(r"[0-9a-f]{40}", harness["commit"])
        assert isinstance(harness["dirty"], bool)

    def it_matches_the_directory_it_was_written_into(experiment, manifest, data_directory):
        experiment()
        [run_directory] = data_directory.iterdir()
        assert run_directory.name.startswith(
            manifest()["timestamp"].replace("-", "").replace(":", "")
        )


def describe_a_run_that_dies():
    @pytest.fixture
    def dead_port(porting_docker, port_result):
        """What the 429 casualties looked like: claude exits 1 after printing its result."""
        port_result.update(
            is_error=True,
            api_error_status=429,
            result="You've hit your monthly spend limit",
        )
        porting_docker.run.side_effect = DockerException(
            ["docker", "container", "run"], 1, stdout=json.dumps(port_result).encode()
        )

    def it_still_raises(experiment, dead_port):
        with pytest.raises(DockerException):
            experiment()

    def it_stamps_completed_at(experiment, manifest, dead_port):
        with pytest.raises(DockerException):
            experiment()
        assert re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", manifest()["completed_at"]
        )

    def it_marks_the_error_with_the_sandbox_message(experiment, manifest, dead_port):
        with pytest.raises(DockerException):
            experiment()
        assert manifest()["error"].startswith(
            "The command executed was `docker container run`.\nIt returned with code 1"
        )

    def it_banks_the_result_the_agent_printed(experiment, data_directory, dead_port):
        with pytest.raises(DockerException):
            experiment()
        [run_directory] = data_directory.iterdir()
        result = json.loads((run_directory / "result.json").read_text())
        assert result["is_error"] is True
        assert result["api_error_status"] == 429

    def it_banks_no_result_when_the_agent_printed_nothing(
        experiment, data_directory, manifest, porting_docker
    ):
        porting_docker.run.side_effect = DockerException(
            ["docker", "container", "run"], 137, stdout=b""
        )
        with pytest.raises(DockerException):
            experiment()
        [run_directory] = data_directory.iterdir()
        assert not (run_directory / "result.json").exists()
        assert manifest()["error"]


def describe_the_container_view():
    def it_binds_the_port_at_the_fixed_container_path(experiment, porting_calls):
        experiment()
        [call] = porting_calls
        targets = [str(target) for _, target, _ in call["volumes"]]
        assert "/workspace/ported_implementation" in targets

    def it_binds_the_reference_at_one_read_only_input(experiment, porting_calls):
        '''Kevin on #77: "tests/ should not be a separate mount."'''
        experiment(include_unit_tests=True, include_target_integration_tests=True)
        [call] = porting_calls
        assert [
            (str(target), mode)
            for _, target, mode in call["volumes"]
            if str(target).startswith("/input")
        ] == [("/input", "ro")]

    def it_stages_the_credentials_the_suite_planted(experiment, porting_calls):
        """A patch that silently missed would bind the real host token instead."""
        experiment()
        [call] = porting_calls
        assert call["credentials"] == '{"fake": "integration-suite"}'

    def it_hides_the_condition_from_the_environment(experiment, porting_calls):
        experiment(include_unit_tests=True, include_source_integration_tests=True)
        [call] = porting_calls
        assert not any("unit-tests" in value for value in call["envs"].values())
        assert not any("integration-tests" in value for value in call["envs"].values())

    def it_hides_the_host_run_directory_from_the_prompt(
        experiment, porting_calls, data_directory
    ):
        experiment()
        [call] = porting_calls
        [run_directory] = data_directory.iterdir()
        assert run_directory.name not in call["prompt"]

    def it_still_builds_the_jail_the_container_joins(experiment, porting_calls):
        experiment()
        [call] = porting_calls
        assert call["envs"]["HTTPS_PROXY"].startswith("http://agent-harness-sandbox-proxy-")


def describe_cli():
    def it_prints_where_the_run_landed(data_directory, porting_docker):
        result = CliRunner().invoke(cli, ["--source-language", "javascript"])
        [run_directory] = data_directory.iterdir()
        assert f"Run directory: {run_directory}" in result.output
