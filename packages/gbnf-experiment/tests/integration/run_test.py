import json
import re
from pathlib import Path

import pytest
from click.testing import CliRunner
from python_on_whales.exceptions import DockerException

from agent_harness_sandbox.agents.ClaudeAgent import ClaudeAgent
from gbnf_experiment import run_gbnf_experiment
from gbnf_experiment.cli import cli
from gbnf_experiment.config import prepare_cache_key, settings
from porting_harness.run_porting_harness import PROMPT_PATH

from conftest import GRAMMAR_FIXTURES

TYPESCRIPT_REFERENCE = [
    "/workspace/reference_implementation/typescript/package.json",
    "/workspace/reference_implementation/typescript/src/index.ts",
]
PYTHON_REFERENCE = [
    "/workspace/reference_implementation/python/gbnf/index.py",
    "/workspace/reference_implementation/python/pyproject.toml",
]
TYPESCRIPT_SUITE = [
    "/workspace/tests/typescript/iteration/grammars_test.typescript",
    "/workspace/tests/typescript/validation/validate_test.typescript",
]
PYTHON_SUITE = [
    *(
        f"/workspace/tests/python/iteration/grammars/{name}.{suffix}"
        for name in GRAMMAR_FIXTURES
        for suffix in ("gbnf", "json")
    ),
    "/workspace/tests/python/iteration/grammars_test.python",
    "/workspace/tests/python/validation/validate_test.python",
]


CONFIG = {
    "source_language": "typescript",
    "include_typescript_tests": False,
    "include_python_tests": False,
    "debug": False,
    "effort": "high",
    "model": "claude-opus-5",
}


@pytest.fixture
def experiment(data_directory, prepare_docker, porting_docker, claude_home):
    def run(**kwargs):
        agent = ClaudeAgent(host_home=claude_home)
        return run_gbnf_experiment(**{"agent": agent, **CONFIG, **kwargs})

    return run


@pytest.fixture
def manifest(data_directory):
    def read() -> dict:
        [run_directory] = data_directory.iterdir()
        return json.loads((run_directory / "manifest.json").read_text())

    return read


def describe_gbnf_experiment():
    def it_caches_the_prepared_corpus_under_the_content_key(
        experiment, prepared_directory
    ):
        experiment()
        assert (prepared_directory / prepare_cache_key).is_dir()

    def it_caches_the_prepared_corpus_outside_the_data_tree(
        experiment, data_directory, prepared_directory
    ):
        """The cache is rebuildable, so it is not part of the run record."""
        experiment()
        assert data_directory not in prepared_directory.parents

    def it_prepares_once_across_conditions(experiment, prepare_docker):
        experiment()
        experiment(include_python_tests=True)
        prepare_docker.run.assert_called_once()

    def it_leaves_no_staging_directory_behind(experiment, prepared_directory):
        experiment()
        assert list(prepared_directory.glob("*.staging")) == []

    def describe_the_assembled_reference():
        @pytest.mark.parametrize(
            ("source_language", "typescript", "python", "expected"),
            [
                ("typescript", False, False, TYPESCRIPT_REFERENCE),
                ("typescript", True, False, [*TYPESCRIPT_REFERENCE, *TYPESCRIPT_SUITE]),
                ("typescript", False, True, [*TYPESCRIPT_REFERENCE, *PYTHON_SUITE]),
                (
                    "typescript",
                    True,
                    True,
                    [*TYPESCRIPT_REFERENCE, *PYTHON_SUITE, *TYPESCRIPT_SUITE],
                ),
                ("python", False, False, PYTHON_REFERENCE),
                ("python", True, False, [*PYTHON_REFERENCE, *TYPESCRIPT_SUITE]),
                ("python", False, True, [*PYTHON_REFERENCE, *PYTHON_SUITE]),
                ("python", True, True, [*PYTHON_REFERENCE, *PYTHON_SUITE, *TYPESCRIPT_SUITE]),
            ],
            ids=[
                "typescript-none",
                "typescript-source-suite",
                "typescript-target-suite",
                "typescript-both",
                "python-none",
                "python-target-suite",
                "python-source-suite",
                "python-both",
            ],
        )
        def it_carries_the_source_and_exactly_the_selected_suites(
            experiment, porting_calls, source_language, typescript, python, expected
        ):
            """Colocated tests and dev/ never appear, whatever the flags say."""
            experiment(
                source_language=source_language,
                include_typescript_tests=typescript,
                include_python_tests=python,
            )
            [call] = porting_calls
            assert call["container_tree"] == expected

        def it_mounts_no_tests_directory_when_neither_suite_is_asked_for(
            experiment, porting_calls
        ):
            experiment()
            [call] = porting_calls
            assert "/workspace/tests" not in [str(target) for _, target, _ in call["volumes"]]

        def it_stages_the_assembly_outside_the_run_record(experiment, data_directory):
            """The corpus is rebuildable from the cache, so no run banks a copy."""
            experiment()
            experiment(include_python_tests=True)
            assert all(
                not (run / "reference_implementation").exists()
                for run in data_directory.iterdir()
            )

        def it_stages_no_input_tree_beside_the_runs(experiment, data_directory):
            """data/ is a flat list of run directories and holds nothing else."""
            experiment()
            experiment(include_python_tests=True)
            assert all(
                re.fullmatch(r"\d{8}T\d{6}Z_[0-9a-f]{8}", path.name) and path.is_dir()
                for path in data_directory.iterdir()
            )

    def describe_the_port():
        def it_sends_the_prompt_rendered_for_the_target_language(
            experiment, porting_calls
        ):
            experiment(source_language="typescript")
            [call] = porting_calls
            assert call["prompt"] == PROMPT_PATH.read_text().format(
                target_language="python"
            )

        def it_renders_the_reverse_direction(experiment, porting_calls):
            experiment(source_language="python")
            [call] = porting_calls
            assert "typescript" in call["prompt"]
            assert "{target_language}" not in call["prompt"]

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
        experiment(include_python_tests=True)
        [run_directory] = data_directory.iterdir()
        assert re.fullmatch(r"\d{8}T\d{6}Z_[0-9a-f]{8}", run_directory.name)

    def it_keeps_consecutive_runs_apart(experiment, data_directory):
        experiment()
        experiment()
        assert len(list(data_directory.iterdir())) == 2

    def it_gives_two_conditions_two_directories(experiment, data_directory):
        experiment(source_language="typescript")
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
    def it_starts_the_container_with_an_empty_output_directory(
        experiment, porting_calls
    ):
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
            "condition",
            "derivation",
            "reference_implementation",
            "sandbox",
            "harness",
        }

    def it_records_the_condition_that_ran(experiment, manifest):
        experiment(
            source_language="python",
            include_typescript_tests=True,
            effort="low",
            model="claude-sonnet-4-5",
        )
        assert manifest()["condition"] == {
            "name": "source-python_typescript-tests_effort-low_model-claude-sonnet-4-5",
            "source_language": "python",
            "target_language": "typescript",
            "include_typescript_tests": True,
            "include_python_tests": False,
            "effort": "low",
            "model": "claude-sonnet-4-5",
        }

    def it_withholds_the_colocated_test_from_the_record_and_the_tree(
        experiment, manifest, porting_calls
    ):
        experiment()
        assert (
            "source/typescript/src/index.test.ts"
            not in manifest()["reference_implementation"]["included"]
        )
        [call] = porting_calls
        assert (
            "/workspace/reference_implementation/typescript/src/index.test.ts"
            not in call["container_tree"]
        )

    def it_records_the_included_paths_from_the_prepared_root(experiment, manifest):
        """One list, one root: source and suite paths side by side."""
        experiment(include_python_tests=True)
        included = manifest()["reference_implementation"]["included"]
        assert "source/typescript/src/index.ts" in included
        assert "tests/python/validation/validate_test.python" in included

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


def staged_reference(call):
    """Where assembly put the corpus, read back off the mount the container got.

    Assembly writes source/ and tests/ under one root; the harness binds those
    at /workspace/reference_implementation and /workspace/tests.
    """
    [source] = [
        Path(source)
        for source, target, _ in call["volumes"]
        if str(target) == "/workspace/reference_implementation"
    ]
    return source.parent


def describe_the_staged_reference_corpus():
    def it_binds_a_staged_copy_not_the_prepared_cache(
        experiment, porting_calls, prepared_directory
    ):
        experiment()
        [call] = porting_calls
        assert prepared_directory not in staged_reference(call).parents

    def it_binds_the_source_and_test_trees_from_one_staging_root(
        experiment, porting_calls
    ):
        experiment(include_python_tests=True)
        [call] = porting_calls
        staged = staged_reference(call)
        sources = [Path(source) for source, _, _ in call["volumes"]]
        assert staged / "source" in sources
        assert staged / "tests" in sources

    def it_throws_the_staged_corpus_away_when_the_run_ends(experiment, porting_calls):
        experiment()
        [call] = porting_calls
        assert not staged_reference(call).exists()


def describe_the_rendered_prompt():
    def it_sends_the_target_language_not_the_template(experiment, porting_calls):
        experiment(source_language="typescript")
        [call] = porting_calls
        assert "python" in call["prompt"]
        assert "{" not in call["prompt"]
        assert "}" not in call["prompt"]


def describe_the_container_view():
    def it_binds_the_port_at_the_fixed_container_path(experiment, porting_calls):
        experiment(include_python_tests=True)
        [call] = porting_calls
        targets = [target for _, target, _ in call["volumes"]]
        assert "/workspace/ported_implementation" in targets

    def it_stages_the_credentials_the_suite_planted(experiment, porting_calls):
        """A patch that silently missed would bind the real host token instead."""
        experiment()
        [call] = porting_calls
        assert call["credentials"] == '{"fake": "integration-suite"}'

    def it_hides_the_condition_from_the_environment(experiment, porting_calls):
        experiment(include_python_tests=True)
        [call] = porting_calls
        assert not any("python-tests" in value for value in call["envs"].values())

    def it_hides_the_host_run_directory_from_the_prompt(experiment, porting_calls, data_directory):
        experiment()
        [call] = porting_calls
        [run_directory] = data_directory.iterdir()
        assert run_directory.name not in call["prompt"]

    def it_still_builds_the_jail_the_container_joins(experiment, porting_calls):
        experiment()
        [call] = porting_calls
        assert call["envs"]["HTTPS_PROXY"].startswith("http://agent-harness-sandbox-proxy-")


def describe_cli():
    def it_prints_where_the_run_landed(
        data_directory, prepare_docker, porting_docker
    ):
        result = CliRunner().invoke(cli, ["--source-language", "typescript"])
        [run_directory] = data_directory.iterdir()
        assert f"Run directory: {run_directory}" in result.output
