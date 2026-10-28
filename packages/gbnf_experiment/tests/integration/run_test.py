import json
import os
import re
from pathlib import Path

import pytest
from click.testing import CliRunner
from botbox import ClaudeAgent, DockerException

from gbnf_experiment import run_gbnf_experiment
from gbnf_experiment.cli import cli
from gbnf_experiment import config

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
    "memory": "8g",
}


@pytest.fixture
def experiment(data_directory, docker_daemon, claude_home):
    async def run(model="claude-opus-5", effort="high", **kwargs):
        """Each call gets a fresh folder, as the runner gives each run one."""
        agent = ClaudeAgent(model=model, effort=effort, host_home=claude_home)
        run_directory = data_directory / f"run-{len(list(data_directory.glob('run-*')))}"
        run_directory.mkdir(parents=True)
        await run_gbnf_experiment(**{"agent": agent, "run_directory": run_directory, **CONFIG, **kwargs})

    return run


@pytest.fixture
def manifest(data_directory):
    def read() -> dict:
        [run_directory] = data_directory.iterdir()
        return json.loads((run_directory / "manifest.json").read_text())

    return read


def prepare_builds(builds) -> list[dict]:
    return [build for build in builds if build["context"] == config.PREPARE_DOCKER_DIRECTORY]


def describe_the_prepare_image():
    async def it_builds_at_the_pinned_commit(experiment, builds):
        await experiment()
        [build] = prepare_builds(builds)
        assert build["build_args"]["GBNF_COMMIT"] == config.GBNF_COMMIT

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
    async def it_builds_with_the_rules_the_condition_composes(experiment, builds, flags, present):
        await experiment(**flags)
        [build] = prepare_builds(builds)
        rules = build["build_args"]["RULES"].splitlines()
        assert "+ /python/gbnf/**.py" in rules
        assert {
            rule
            for rule in (UNIT_RULE, SOURCE_INTEGRATION_RULE, TARGET_INTEGRATION_RULE)
            if rule in rules
        } == present

    async def it_extracts_shared_into_the_cache_as_the_current_user(
        experiment, builds, prepare_calls, prepared_directory
    ):
        await experiment()
        [build] = prepare_builds(builds)
        [call] = prepare_calls
        assert call["image"] == build["tags"]
        assert call["command"] == ["cp", "-a", "/shared/.", "/prepared-output/"]
        assert call["user"] == f"{os.getuid()}:{os.getgid()}"
        assert prepared_directory in volume_source(call["volumes"], "/prepared-output").parents

    async def it_prepares_a_condition_once(experiment, prepare_calls):
        await experiment()
        await experiment()
        assert len(prepare_calls) == 1

    async def it_prepares_each_condition_into_its_own_image_and_cache_entry(
        experiment, builds, prepared_directory
    ):
        await experiment()
        await experiment(include_unit_tests=True)
        assert len({build["tags"] for build in prepare_builds(builds)}) == 2
        assert len(list(prepared_directory.iterdir())) == 2

    async def it_leaves_no_staging_directory_behind(experiment, prepared_directory):
        await experiment()
        assert list(prepared_directory.glob("*.staging")) == []

    async def it_caches_outside_the_data_tree(experiment, data_directory, prepared_directory):
        """The cache is rebuildable, so it is not part of the run record."""
        await experiment()
        assert data_directory not in prepared_directory.parents


def describe_the_source():
    async def it_mounts_the_extracted_shared_tree_read_only(
        experiment, porting_calls, prepared_directory
    ):
        await experiment()
        [call] = porting_calls
        [(source, mode)] = [
            (Path(source), mode) for source, target, mode in call["volumes"] if target == "/input"
        ]
        assert source.parent == prepared_directory
        assert mode == "ro"

    async def it_shows_the_agent_shared_unchanged(experiment, porting_calls):
        await experiment()
        [call] = porting_calls
        assert call["container_tree"] == [f"/input/{name}" for name in SHARED]

    async def it_records_every_file_the_agent_was_shown(experiment, manifest):
        await experiment()
        assert manifest()["reference_implementation"]["included"] == list(SHARED)

    async def it_stages_no_input_tree_beside_the_runs(experiment, data_directory):
        """data/ is a flat list of run directories and holds nothing else."""
        await experiment()
        await experiment(include_unit_tests=True)
        assert sorted(path.name for path in data_directory.iterdir()) == ["run-0", "run-1"]


def describe_the_port():
        async def it_sends_its_own_prompt_inside_the_harness_frame(
            experiment, porting_calls
        ):
            await experiment(source_language="javascript")
            [call] = porting_calls
            assert call["prompt"].endswith(
                "\n\n"
                + UPSTREAM_PROMPT.format(
                    source_language="javascript", target_language="python"
                )
                + "\n"
            )

        async def it_renders_the_reverse_direction(experiment, porting_calls):
            await experiment(source_language="python")
            [call] = porting_calls
            assert call["prompt"].endswith(
                "\n\n"
                + UPSTREAM_PROMPT.format(
                    source_language="python", target_language="typescript"
                )
                + "\n"
            )

        async def it_names_where_each_included_suite_sits(experiment, porting_calls):
            await experiment(
                source_language="python",
                include_unit_tests=True,
                include_source_integration_tests=True,
                include_target_integration_tests=True,
            )
            [call] = porting_calls
            assert call["prompt"].endswith("\n\n" + UPSTREAM_PROMPT_WITH_EVERY_SUITE + "\n")

        async def it_names_where_each_included_suite_sits_from_javascript(experiment, porting_calls):
            await experiment(
                source_language="javascript",
                include_unit_tests=True,
                include_source_integration_tests=True,
                include_target_integration_tests=True,
            )
            [call] = porting_calls
            assert call["prompt"].endswith(
                "\n\n" + UPSTREAM_PROMPT_WITH_EVERY_SUITE_FROM_JAVASCRIPT + "\n"
            )

        async def it_collects_the_port_into_the_run_directory(experiment, data_directory):
            await experiment()
            [run_directory] = data_directory.iterdir()
            assert (run_directory / "ported_implementation" / "ported.py").is_file()

        async def it_pins_the_model_in_the_argv_the_container_runs(
            experiment, porting_calls
        ):
            await experiment(model="claude-sonnet-4-5")
            [call] = porting_calls
            command = call["command"]
            assert command[command.index("--model") + 1] == "claude-sonnet-4-5"


def describe_the_run_directory():
    async def it_writes_into_the_folder_it_was_given(experiment, data_directory):
        await experiment()
        [run_directory] = data_directory.iterdir()
        assert run_directory.name == "run-0"
        assert sorted(path.name for path in run_directory.iterdir()) == [
            "manifest.json",
            "ported_implementation",
            "proxy.log",
            "result.json",
            "stderr.txt",
            "transcript",
        ]

    async def it_runs_the_agent_container_once(experiment, porting_calls):
        await experiment()
        assert len(porting_calls) == 1

    async def it_banks_the_proxy_log_the_box_returned(experiment, data_directory):
        await experiment()
        [run_directory] = data_directory.iterdir()
        assert (run_directory / "proxy.log").read_text() == PROXY_LOG

    async def it_banks_the_transcript_at_its_path_under_the_agent_home(experiment, data_directory):
        await experiment()
        [run_directory] = data_directory.iterdir()
        assert (run_directory / "transcript" / TRANSCRIPT_PATH).read_text() == TRANSCRIPT


def describe_the_clean_slate():
    async def it_starts_the_container_with_an_empty_output_directory(
        experiment, porting_calls
    ):
        await experiment()
        [call] = porting_calls
        assert not any(path.startswith("/target") for path in call["container_tree"])

    async def it_hides_one_run_s_output_from_the_next(
        experiment, porting_calls, data_directory
    ):
        await experiment()
        await experiment()
        ports = list(data_directory.glob("*/ported_implementation/ported.py"))
        assert len(ports) == 2
        _, second = porting_calls
        assert not any(path.startswith("/target") for path in second["container_tree"])


def describe_the_manifest():
    async def it_lands_in_the_run_directory(experiment, manifest):
        await experiment()
        assert set(manifest()) == {
            "timestamp",
            "completed_at",
            "exit_code",
            "oom_killed",
            "condition",
            "derivation",
            "reference_implementation",
            "sandbox",
            "harness",
        }

    @pytest.mark.parametrize("killed", [True, False, None])
    async def it_records_the_box_s_oom_record_as_is(experiment, manifest, oom_killed, killed):
        oom_killed[0] = killed
        await experiment()
        assert manifest()["oom_killed"] is killed

    async def it_records_the_condition_that_ran(experiment, manifest):
        await experiment(
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

    async def it_records_the_pinned_commit(experiment, manifest):
        await experiment()
        assert manifest()["derivation"] == {"gbnf_commit": config.GBNF_COMMIT}

    async def it_identifies_the_sandbox_by_image_id_alone(
        experiment, manifest, sandbox_image_id
    ):
        """The tag is a constant, so only the id says which image ran."""
        await experiment()
        assert manifest()["sandbox"] == {"image_id": sandbox_image_id}

    async def it_records_one_commit_for_the_whole_harness(experiment, manifest):
        await experiment()
        harness = manifest()["harness"]
        assert re.fullmatch(r"[0-9a-f]{40}", harness["commit"])
        assert isinstance(harness["dirty"], bool)


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

    async def it_raises_with_the_agent_s_error_text(experiment, dead_port):
        with pytest.raises(Exception, match="You've hit your monthly spend limit"):
            await experiment()

    async def it_banks_the_result_the_agent_printed(experiment, data_directory, dead_port):
        with pytest.raises(Exception):
            await experiment()
        [run_directory] = data_directory.iterdir()
        result = json.loads((run_directory / "result.json").read_text())
        assert result["is_error"] is True
        assert result["api_error_status"] == 429

    async def it_banks_the_transcript_and_proxy_log(experiment, data_directory, dead_port):
        with pytest.raises(Exception):
            await experiment()
        [run_directory] = data_directory.iterdir()
        assert (run_directory / "transcript" / TRANSCRIPT_PATH).read_text() == TRANSCRIPT
        assert (run_directory / "proxy.log").read_text() == PROXY_LOG

    async def it_records_the_error_text_in_the_manifest(experiment, manifest, dead_port):
        with pytest.raises(Exception):
            await experiment()
        assert manifest()["error"] == "You've hit your monthly spend limit"

    async def it_records_the_exit_code_in_the_manifest(experiment, manifest, dead_port):
        with pytest.raises(Exception):
            await experiment()
        assert manifest()["exit_code"] == 1

    async def it_banks_the_agent_s_stderr_beside_the_result(
        experiment, data_directory, dead_port, agent_stderr
    ):
        agent_stderr[0] = "Error: 429\n"
        with pytest.raises(Exception):
            await experiment()
        [run_directory] = data_directory.iterdir()
        assert (run_directory / "stderr.txt").read_text() == "Error: 429\n"


def describe_a_run_that_raises():
    @pytest.fixture
    def failed_build(box_error):
        """The agent image build fails, so port_codebase raises before any container starts."""
        box_error.append(DockerException(["docker", "build"], 1, ""))

    async def it_still_raises(experiment, failed_build):
        with pytest.raises(DockerException):
            await experiment()

    async def it_stamps_completed_at(experiment, manifest, failed_build):
        with pytest.raises(DockerException):
            await experiment()
        assert re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", manifest()["completed_at"]
        )

    async def it_marks_the_error(experiment, manifest, failed_build):
        with pytest.raises(DockerException):
            await experiment()
        assert manifest()["error"].startswith("`docker build` exited 1")

    async def it_banks_no_result(experiment, data_directory, failed_build):
        with pytest.raises(DockerException):
            await experiment()
        [run_directory] = data_directory.iterdir()
        assert not (run_directory / "result.json").exists()

    async def it_records_no_exit_code(experiment, manifest, failed_build):
        with pytest.raises(DockerException):
            await experiment()
        assert "exit_code" not in manifest()


def describe_the_rendered_prompt():
    async def it_sends_the_target_language_not_the_template(experiment, porting_calls):
        await experiment(source_language="javascript")
        [call] = porting_calls
        assert "python" in call["prompt"]
        # The Dockerfiles quoted in the prompt carry braces of their own, so look for the placeholders.
        assert "{source_language}" not in call["prompt"]
        assert "{target_language}" not in call["prompt"]
        assert "{suites_information}" not in call["prompt"]

    async def it_calls_javascript_typescript(experiment, porting_calls):
        await experiment(source_language="python", include_target_integration_tests=True)
        [call] = porting_calls
        assert " to typescript.\n" in call["prompt"]
        assert "- typescript integration tests:" in call["prompt"]


def describe_the_container_view():
    async def it_hides_the_host_run_directory_from_the_prompt(experiment, porting_calls, data_directory):
        await experiment()
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

    @pytest.fixture
    def working_folder(tmp_path, monkeypatch):
        folder = tmp_path / "elsewhere"
        folder.mkdir()
        monkeypatch.chdir(folder)
        return folder

    @pytest.fixture
    def output(data_directory):
        return data_directory / "tests-configuration" / "brave-otter"

    def it_writes_the_run_into_the_output(home, working_folder, output, docker_daemon):
        result = CliRunner().invoke(cli, ["--source-language", "javascript", "--output", str(output)])
        assert result.exit_code == 0, result.output
        assert (output / "manifest.json").is_file()
        assert (output / "ported_implementation" / "ported.py").is_file()
        assert list(output.parent.iterdir()) == [output]
        assert list(working_folder.iterdir()) == []

    def it_caps_the_box_at_8g_by_default(home, working_folder, output, docker_daemon, boxes):
        result = CliRunner().invoke(cli, ["--source-language", "javascript", "--output", str(output)])
        assert result.exit_code == 0, result.output
        assert [box["memory"] for box in boxes] == ["8g"]

    def it_caps_the_box_at_the_memory_given(home, working_folder, output, docker_daemon, boxes):
        result = CliRunner().invoke(
            cli, ["--source-language", "javascript", "--memory", "4g", "--output", str(output)]
        )
        assert result.exit_code == 0, result.output
        assert [box["memory"] for box in boxes] == ["4g"]

    def it_prepares_the_condition_its_flags_name(home, working_folder, output, docker_daemon, builds):
        CliRunner().invoke(
            cli,
            [
                "--source-language", "python", "--include-target-integration-tests", "1",
                "--include-unit-tests", "0", "--output", str(output),
            ],
        )
        [build] = prepare_builds(builds)
        assert TARGET_INTEGRATION_RULE in build["build_args"]["RULES"].splitlines()
        assert UNIT_RULE not in build["build_args"]["RULES"].splitlines()

    def it_exits_non_zero_when_the_agent_exits_non_zero(home, working_folder, output, docker_daemon, exit_code):
        exit_code[0] = 1
        result = CliRunner().invoke(cli, ["--source-language", "javascript", "--output", str(output)])
        assert result.exit_code != 0
        assert json.loads((output / "manifest.json").read_text())["exit_code"] == 1

    def it_exits_non_zero_when_the_result_is_an_error(home, working_folder, output, docker_daemon, port_result):
        """claude can exit 0 with is_error set; such a run must not count."""
        port_result.update(is_error=True)
        result = CliRunner().invoke(cli, ["--source-language", "javascript", "--output", str(output)])
        assert result.exit_code != 0

    def it_exits_one_with_the_agent_s_error_text_uncaught(home, working_folder, output, docker_daemon, port_result):
        port_result.update(is_error=True, api_error_status=429, result="API Error: 429 rate limited")
        result = CliRunner().invoke(cli, ["--source-language", "javascript", "--output", str(output)])
        assert result.exit_code == 1
        assert "API Error: 429 rate limited" in str(result.exception)
        assert (output / "result.json").is_file()
