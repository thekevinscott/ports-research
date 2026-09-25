from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from porting_harness.run_porting_harness import PROMPT_PATH, run_porting_harness

OPTIONS = (
    "agent",
    "image",
    "target_language",
    "output_directory",
    "debug",
    "effort",
    "model",
    "transcripts",
    "proxy_log",
)


@pytest.fixture
def run_agent_harness_sandbox():
    with patch(
        "porting_harness.run_porting_harness.run_agent_harness_sandbox", autospec=True
    ) as mock:
        mock.return_value = "container output"
        yield mock


@pytest.fixture
def render_prompt():
    with patch(
        "porting_harness.run_porting_harness.render_prompt", autospec=True
    ) as mock:
        mock.return_value = "Port it to python.\n"
        yield mock


@pytest.fixture
def output_directory(tmp_path):
    return tmp_path / "ported_implementation"


@pytest.fixture
def agent():
    return Mock(name="agent")


@pytest.fixture
def options(agent, output_directory, tmp_path):
    def build(**overrides):
        return {
            "agent": agent,
            "image": "a-workspace:abc",
            "target_language": "python",
            "output_directory": output_directory,
            "debug": False,
            "effort": "high",
            "model": "claude-opus-5",
            "transcripts": tmp_path / "transcript",
            "proxy_log": tmp_path / "proxy.log",
            **overrides,
        }

    return build


def describe_signature():
    @pytest.mark.parametrize("option", list(OPTIONS))
    def it_requires_every_option(options, option):
        with pytest.raises(TypeError):
            run_porting_harness(**{k: v for k, v in options().items() if k != option})

    def it_takes_no_positional_argument(options):
        with pytest.raises(TypeError):
            run_porting_harness(*options().values())


def describe_run_porting_harness():
    def it_creates_a_missing_output_directory(run_agent_harness_sandbox, options, tmp_path):
        nested_output_directory = tmp_path / "nested" / "ported_implementation"

        run_porting_harness(**options(output_directory=nested_output_directory))

        assert nested_output_directory.is_dir()

    def it_accepts_an_existing_output_directory(
        run_agent_harness_sandbox, options, output_directory
    ):
        output_directory.mkdir()

        run_porting_harness(**options())

        assert output_directory.is_dir()

    def it_wires_the_image_the_mount_and_home_into_the_sandbox(
        run_agent_harness_sandbox,
        options,
        agent,
        output_directory,
        tmp_path,
    ):
        run_porting_harness(**options())

        assert run_agent_harness_sandbox.call_args.kwargs == {
            "agent": agent,
            "image": "a-workspace:abc",
            "inputs": {},
            "outputs": {output_directory: Path("/workspace/ported_implementation")},
            "envs": {},
            "debug": False,
            "home": Path("/workspace"),
            "effort": "high",
            "model": "claude-opus-5",
            "transcripts": tmp_path / "transcript",
            "proxy_log": tmp_path / "proxy.log",
        }

    def it_mounts_nothing_in(run_agent_harness_sandbox, options):
        """The reference is in the image; a mount could show the agent something else."""
        run_porting_harness(**options())

        assert run_agent_harness_sandbox.call_args.kwargs["inputs"] == {}

    def it_runs_the_image_the_caller_built(run_agent_harness_sandbox, options):
        run_porting_harness(**options(image="another:def"))

        assert run_agent_harness_sandbox.call_args.kwargs["image"] == "another:def"

    def it_binds_the_directory_the_caller_named(
        run_agent_harness_sandbox, options, output_directory
    ):
        """The port is synced there live, so a crashed run still leaves what it wrote."""
        run_porting_harness(**options())

        assert list(run_agent_harness_sandbox.call_args.kwargs["outputs"]) == [output_directory]

    def it_forwards_the_agent_without_choosing_one(run_agent_harness_sandbox, options):
        """Which harness runs the port is the caller's experiment design, not the harness's."""
        chosen = Mock(name="chosen")

        run_porting_harness(**options(agent=chosen))

        assert run_agent_harness_sandbox.call_args.kwargs["agent"] is chosen

    def it_forwards_debug(run_agent_harness_sandbox, options):
        run_porting_harness(**options(debug=True))

        assert run_agent_harness_sandbox.call_args.kwargs["debug"] is True

    def it_forwards_the_effort(run_agent_harness_sandbox, options):
        run_porting_harness(**options(effort="max"))

        assert run_agent_harness_sandbox.call_args.kwargs["effort"] == "max"

    def it_forwards_the_model(run_agent_harness_sandbox, options):
        run_porting_harness(**options(model="claude-sonnet-4-5"))

        assert run_agent_harness_sandbox.call_args.kwargs["model"] == "claude-sonnet-4-5"

    def it_forwards_the_transcripts_directory(run_agent_harness_sandbox, options, tmp_path):
        transcripts = tmp_path / "elsewhere"

        run_porting_harness(**options(transcripts=transcripts))

        assert run_agent_harness_sandbox.call_args.kwargs["transcripts"] == transcripts

    def it_forwards_the_proxy_log_destination(run_agent_harness_sandbox, options, tmp_path):
        proxy_log = tmp_path / "elsewhere.log"

        run_porting_harness(**options(proxy_log=proxy_log))

        assert run_agent_harness_sandbox.call_args.kwargs["proxy_log"] == proxy_log

    def it_sends_its_own_prompt_and_returns_the_output(
        run_agent_harness_sandbox, render_prompt, options
    ):
        """The caller names a direction; the wording is the harness's."""
        claude_output = run_porting_harness(**options())

        render_prompt.assert_called_once_with(PROMPT_PATH, "python")
        assert run_agent_harness_sandbox.call_args.args == (render_prompt.return_value,)
        assert claude_output == "container output"

    def it_renders_the_direction_the_caller_asked_for(
        run_agent_harness_sandbox, render_prompt, options
    ):
        run_porting_harness(**options(target_language="typescript"))

        render_prompt.assert_called_once_with(PROMPT_PATH, "typescript")


def describe_the_packaged_prompt():
    def it_ships_a_template_with_the_target_language_left_open():
        """The prompt is this package's contribution, so it ships inside it."""
        assert "{target_language}" in PROMPT_PATH.read_text()
