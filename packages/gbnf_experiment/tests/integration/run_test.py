import json
import os
import re
from pathlib import Path

import pytest
from click.testing import CliRunner
from botbox import ClaudeAgent
from python_on_whales import docker
from python_on_whales.exceptions import DockerException

from gbnf_experiment import run_gbnf_experiment
from gbnf_experiment.cli import cli
from gbnf_experiment.config import settings

from conftest import (
    FAKE_CREDENTIALS,
    PROXY_LOG,
    SHARED,
    TRANSCRIPT,
    TRANSCRIPT_PATH,
    volume_source,
)

# Spelled out rather than imported: a reworded prompt has to move the expected
# text here too, or the two sides drift together and prove nothing.
UPSTREAM_PROMPT = (
    "Port the implementation under {source_language}/ to {target_language}.\n"
)
UPSTREAM_PROMPT_WITH_EVERY_SUITE = (
    "Port the implementation under python/ to typescript.\n"
    "\n"
    "The following test suites are included:\n"
    "\n"
    "- python unit tests: python/gbnf/ (colocated, *_test.py)\n"
    "- python integration tests: python/tests/generated/\n"
    "- typescript integration tests: javascript/integration-tests/generated/\n"
)
UPSTREAM_PROMPT_WITH_EVERY_SUITE_FROM_JAVASCRIPT = (
    "Port the implementation under javascript/ to python.\n"
    "\n"
    "The following test suites are included:\n"
    "\n"
    "- typescript unit tests: javascript/src/ (colocated, *.test.ts)\n"
    "- typescript integration tests: javascript/integration-tests/generated/\n"
    "- python integration tests: python/tests/generated/\n"
)
# One line from each test rule file, as it reaches the image in RULES.
UNIT_RULE = "+ /python/gbnf/**_test.py"
SOURCE_INTEGRATION_RULE = "+ /python/tests/***"
TARGET_INTEGRATION_RULE = "+ /javascript/integration-tests/***"


CONFIG = {
    "source_language": "python",
    "include_unit_tests": False,
    "include_source_integration_tests": False,
    "include_target_integration_tests": False,
    "debug": False,
}


@pytest.fixture
def experiment(data_directory, docker_daemon, claude_home):
    def run(model="claude-opus-5", effort="high", **kwargs):
        agent = ClaudeAgent(model=model, effort=effort, host_home=claude_home)
        return run_gbnf_experiment(**{"agent": agent, **CONFIG, **kwargs})

    return run


@pytest.fixture
def manifest(data_directory):
    def read() -> dict:
        [run_directory] = data_directory.iterdir()
        return json.loads((run_directory / "manifest.json").read_text())

    return read


def prepare_builds(builds) -> list[dict]:
    return [build for build in builds if build["context"] == settings.prepare_docker_directory]


def describe_the_prepare_image():
    def it_builds_at_the_pinned_commit(experiment, builds):
        experiment()
        [build] = prepare_builds(builds)
        assert build["build_args"]["GBNF_COMMIT"] == settings.gbnf_commit

    @pytest.mark.parametrize(
        ("flags", "present"),
        [
            ({}, set()),
            ({"include_unit_tests": True}, {UNIT_RULE}),
            ({"include_source_integration_tests": True}, {SOURCE_INTEGRATION_RULE}),
            ({"include_target_integration_tests": True}, {TARGET_INTEGRATION_RULE}),
            (
                {
                    "include_unit_tests": True,
                    "include_source_integration_tests": True,
                    "include_target_integration_tests": True,
                },
                {UNIT_RULE, SOURCE_INTEGRATION_RULE, TARGET_INTEGRATION_RULE},
            ),
        ],
        ids=["none", "unit", "source-integration", "target-integration", "all"],
    )
    def it_builds_with_the_rules_the_condition_composes(experiment, builds, flags, present):
        experiment(**flags)
        [build] = prepare_builds(builds)
        rules = build["build_args"]["RULES"].splitlines()
        assert "+ /python/gbnf/**.py" in rules
        assert {
            rule
            for rule in (UNIT_RULE, SOURCE_INTEGRATION_RULE, TARGET_INTEGRATION_RULE)
            if rule in rules
        } == present

    def it_extracts_shared_into_the_cache_as_the_current_user(
        experiment, builds, prepare_calls, prepared_directory
    ):
        experiment()
        [build] = prepare_builds(builds)
        [call] = prepare_calls
        assert call["image"] == build["tags"]
        assert call["command"] == ["cp", "-a", "/shared/.", "/prepared-output/"]
        assert call["user"] == f"{os.getuid()}:{os.getgid()}"
        assert prepared_directory in volume_source(call["volumes"], "/prepared-output").parents

    def it_prepares_a_condition_once(experiment, prepare_calls):
        experiment()
        experiment()
        assert len(prepare_calls) == 1

    def it_prepares_each_condition_into_its_own_image_and_cache_entry(
        experiment, builds, prepared_directory
    ):
        experiment()
        experiment(include_unit_tests=True)
        assert len({build["tags"] for build in prepare_builds(builds)}) == 2
        assert len(list(prepared_directory.iterdir())) == 2

    def it_leaves_no_staging_directory_behind(experiment, prepared_directory):
        experiment()
        assert list(prepared_directory.glob("*.staging")) == []

    def it_caches_outside_the_data_tree(experiment, data_directory, prepared_directory):
        """The cache is rebuildable, so it is not part of the run record."""
        experiment()
        assert data_directory not in prepared_directory.parents


def describe_the_source():
    def it_mounts_the_extracted_shared_tree_read_only(
        experiment, porting_calls, prepared_directory
    ):
        experiment()
        [call] = porting_calls
        [(source, mode)] = [
            (Path(source), mode) for source, target, mode in call["volumes"] if target == "/input"
        ]
        assert source.parent == prepared_directory
        assert mode == "ro"

    def it_shows_the_agent_shared_unchanged(experiment, porting_calls):
        experiment()
        [call] = porting_calls
        assert call["container_tree"] == [f"/input/{name}" for name in SHARED]

    def it_records_every_file_the_agent_was_shown(experiment, manifest):
        experiment()
        assert manifest()["reference_implementation"]["included"] == list(SHARED)

    def it_stages_no_input_tree_beside_the_runs(experiment, data_directory):
        """data/ is a flat list of run directories and holds nothing else."""
        experiment()
        experiment(include_unit_tests=True)
        assert all(
            re.fullmatch(r"\d{8}T\d{6}Z_[0-9a-f]{8}", path.name) and path.is_dir()
            for path in data_directory.iterdir()
        )


def describe_the_port():
        def it_sends_its_own_prompt_inside_the_harness_frame(
            experiment, porting_calls
        ):
            experiment(source_language="javascript")
            [call] = porting_calls
            assert call["prompt"].endswith(
                "\n\n"
                + UPSTREAM_PROMPT.format(
                    source_language="javascript", target_language="python"
                )
                + "\n"
            )

        def it_renders_the_reverse_direction(experiment, porting_calls):
            experiment(source_language="python")
            [call] = porting_calls
            assert call["prompt"].endswith(
                "\n\n"
                + UPSTREAM_PROMPT.format(
                    source_language="python", target_language="typescript"
                )
                + "\n"
            )

        def it_names_where_each_included_suite_sits(experiment, porting_calls):
            experiment(
                source_language="python",
                include_unit_tests=True,
                include_source_integration_tests=True,
                include_target_integration_tests=True,
            )
            [call] = porting_calls
            assert call["prompt"].endswith("\n\n" + UPSTREAM_PROMPT_WITH_EVERY_SUITE + "\n")

        def it_names_where_each_included_suite_sits_from_javascript(experiment, porting_calls):
            experiment(
                source_language="javascript",
                include_unit_tests=True,
                include_source_integration_tests=True,
                include_target_integration_tests=True,
            )
            [call] = porting_calls
            assert call["prompt"].endswith(
                "\n\n" + UPSTREAM_PROMPT_WITH_EVERY_SUITE_FROM_JAVASCRIPT + "\n"
            )

        def it_collects_the_port_into_the_run_directory(experiment, data_directory):
            experiment()
            [run_directory] = data_directory.iterdir()
            assert (run_directory / "ported_implementation" / "ported.py").is_file()

        def it_pins_the_model_in_the_argv_the_container_runs(
            experiment, porting_calls
        ):
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

    def it_keeps_consecutive_runs_apart(experiment, data_directory):
        experiment()
        experiment()
        assert len(list(data_directory.iterdir())) == 2

    def it_gives_two_conditions_two_directories(experiment, data_directory):
        experiment(source_language="javascript")
        experiment(source_language="python")
        assert len(list(data_directory.iterdir())) == 2

    def it_runs_the_agent_container_once(experiment, porting_calls):
        experiment()
        assert len(porting_calls) == 1

    def it_banks_the_proxy_log_the_box_returned(experiment, data_directory):
        experiment()
        [run_directory] = data_directory.iterdir()
        assert (run_directory / "proxy.log").read_text() == PROXY_LOG

    def it_banks_the_transcript_at_its_path_under_the_agent_home(experiment, data_directory):
        experiment()
        [run_directory] = data_directory.iterdir()
        assert (run_directory / "transcript" / TRANSCRIPT_PATH).read_text() == TRANSCRIPT


def describe_the_clean_slate():
    def it_starts_the_container_with_an_empty_output_directory(
        experiment, porting_calls
    ):
        experiment()
        [call] = porting_calls
        assert not any(path.startswith("/target") for path in call["container_tree"])

    def it_hides_one_run_s_output_from_the_next(
        experiment, porting_calls, data_directory
    ):
        experiment()
        experiment()
        ports = list(data_directory.glob("*/ported_implementation/ported.py"))
        assert len(ports) == 2
        _, second = porting_calls
        assert not any(path.startswith("/target") for path in second["container_tree"])


def describe_the_manifest():
    def it_lands_in_the_run_directory(experiment, manifest):
        experiment()
        assert set(manifest()) == {
            "timestamp",
            "completed_at",
            "exit_code",
            "condition",
            "derivation",
            "reference_implementation",
            "sandbox",
            "harness",
        }

    def it_records_the_condition_that_ran(experiment, manifest):
        experiment(
            source_language="python",
            include_target_integration_tests=True,
            effort="low",
            model="claude-sonnet-4-5",
        )
        assert manifest()["condition"] == {
            "name": "source-python_target-integration-tests_effort-low_model-claude-sonnet-4-5",
            "source_language": "python",
            "target_language": "javascript",
            "include_unit_tests": False,
            "include_source_integration_tests": False,
            "include_target_integration_tests": True,
            "effort": "low",
            "model": "claude-sonnet-4-5",
        }

    def it_records_the_pinned_commit(experiment, manifest):
        experiment()
        assert manifest()["derivation"] == {"gbnf_commit": settings.gbnf_commit}

    def it_identifies_the_sandbox_by_image_id_alone(
        experiment, manifest, sandbox_image_id
    ):
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


def describe_a_run_that_exits_non_zero():
    @pytest.fixture
    def dead_port(port_result, exit_code):
        """What the 429 casualties looked like: claude exits 1 after printing its result."""
        port_result.update(
            is_error=True,
            api_error_status=429,
            result="You've hit your monthly spend limit",
        )
        exit_code[0] = 1

    def it_banks_the_result_the_agent_printed(experiment, data_directory, dead_port):
        experiment()
        [run_directory] = data_directory.iterdir()
        result = json.loads((run_directory / "result.json").read_text())
        assert result["is_error"] is True
        assert result["api_error_status"] == 429

    def it_records_no_error_in_the_manifest(experiment, manifest, dead_port):
        experiment()
        assert "error" not in manifest()

    def it_records_the_exit_code_in_the_manifest(experiment, manifest, dead_port):
        experiment()
        assert manifest()["exit_code"] == 1

    def it_banks_the_agent_s_stderr_beside_the_result(
        experiment, data_directory, dead_port, agent_stderr
    ):
        agent_stderr[0] = b"Error: 429\n"
        experiment()
        [run_directory] = data_directory.iterdir()
        assert (run_directory / "stderr.txt").read_text() == "Error: 429\n"


def describe_a_run_that_raises():
    @pytest.fixture
    def failed_build(docker_daemon, builds):
        """The agent image build fails, so port_codebase raises before any container starts."""

        def fail_unless_prepare(context, **options):
            builds.append({"context": Path(context), **options})
            if Path(context) != settings.prepare_docker_directory:
                raise DockerException(["docker", "build"], 1)

        docker.build.side_effect = fail_unless_prepare

    def it_still_raises(experiment, failed_build):
        with pytest.raises(DockerException):
            experiment()

    def it_stamps_completed_at(experiment, manifest, failed_build):
        with pytest.raises(DockerException):
            experiment()
        assert re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", manifest()["completed_at"]
        )

    def it_marks_the_error(experiment, manifest, failed_build):
        with pytest.raises(DockerException):
            experiment()
        assert manifest()["error"].startswith(
            "The command executed was `docker build`.\nIt returned with code 1"
        )

    def it_banks_no_result(experiment, data_directory, failed_build):
        with pytest.raises(DockerException):
            experiment()
        [run_directory] = data_directory.iterdir()
        assert not (run_directory / "result.json").exists()

    def it_records_no_exit_code(experiment, manifest, failed_build):
        with pytest.raises(DockerException):
            experiment()
        assert "exit_code" not in manifest()


def describe_the_rendered_prompt():
    def it_sends_the_target_language_not_the_template(experiment, porting_calls):
        experiment(source_language="javascript")
        [call] = porting_calls
        assert "python" in call["prompt"]
        assert "{" not in call["prompt"]
        assert "}" not in call["prompt"]

    def it_calls_javascript_typescript(experiment, porting_calls):
        experiment(source_language="python", include_target_integration_tests=True)
        [call] = porting_calls
        assert " to typescript.\n" in call["prompt"]
        assert "- typescript integration tests:" in call["prompt"]


def describe_the_container_view():
    def it_stages_the_credentials_the_suite_planted(experiment, porting_calls):
        """A patch that silently missed would bind the real host token instead."""
        experiment()
        [call] = porting_calls
        assert call["credentials"] == FAKE_CREDENTIALS

    def it_hides_the_host_run_directory_from_the_prompt(experiment, porting_calls, data_directory):
        experiment()
        [call] = porting_calls
        [run_directory] = data_directory.iterdir()
        assert run_directory.name not in call["prompt"]


def describe_cli():
    @pytest.fixture
    def home(tmp_path, monkeypatch):
        """ClaudeAgent() reads credentials from ~/.claude; point ~ at a throwaway."""
        home = tmp_path / "home"
        (home / ".claude").mkdir(parents=True)
        (home / ".claude" / ".credentials.json").write_text(FAKE_CREDENTIALS)
        monkeypatch.setenv("HOME", str(home))

    def it_prints_where_the_run_landed(
        home, data_directory, docker_daemon
    ):
        result = CliRunner().invoke(cli, ["--source-language", "javascript"])
        [run_directory] = data_directory.iterdir()
        assert f"Run directory: {run_directory}" in result.output

    def it_prepares_the_condition_its_flags_name(home, data_directory, docker_daemon, builds):
        CliRunner().invoke(
            cli,
            ["--source-language", "python", "--include-target-integration-tests"],
        )
        [build] = prepare_builds(builds)
        assert TARGET_INTEGRATION_RULE in build["build_args"]["RULES"].splitlines()
        assert UNIT_RULE not in build["build_args"]["RULES"].splitlines()
