from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from .run_porting_harness import INPUT_CONTEXT, PROMPT_PATH, run_porting_harness

OPTIONS = (
    "agent",
    "prompt",
    "input",
    "output_directory",
    "debug",
    "effort",
    "model",
    "transcripts",
    "proxy_log",
)


@pytest.fixture
def run_agent_harness_sandbox(build_agent_image):
    with patch(
        "porting_harness.run_porting_harness.run_agent_harness_sandbox", autospec=True
    ) as mock:
        mock.return_value = "container output"
        yield mock


@pytest.fixture
def build_agent_image():
    with patch(
        "porting_harness.run_porting_harness.build_agent_image", autospec=True
    ) as mock:
        mock.return_value = "an-agent:latest"
        yield mock


@pytest.fixture
def input_directory(tmp_path):
    directory = tmp_path / "input"
    directory.mkdir()
    return directory


@pytest.fixture
def output_directory(tmp_path):
    return tmp_path / "ported_implementation"


@pytest.fixture
def agent():
    return Mock(name="agent")


@pytest.fixture
def prompt_class():
    with patch("porting_harness.run_porting_harness.Prompt", autospec=True) as mock:
        mock.return_value.__str__ = Mock(return_value="the rendered prompt")
        yield mock


@pytest.fixture
def options(agent, input_directory, output_directory, tmp_path):
    def build(**overrides):
        return {
            "agent": agent,
            "prompt": "Port /input/python to typescript.\n",
            "input": input_directory,
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

    def it_wires_the_output_and_home_into_the_sandbox(
        run_agent_harness_sandbox,
        options,
        agent,
        output_directory,
        tmp_path,
    ):
        run_porting_harness(**options())

        assert run_agent_harness_sandbox.call_args.kwargs == {
            "agent": agent,
            "image": "an-agent:latest",
            "outputs": {output_directory: Path("/target")},
            "envs": {},
            "debug": False,
            "home": Path("/workspace"),
            "effort": "high",
            "model": "claude-opus-5",
            "transcripts": tmp_path / "transcript",
            "proxy_log": tmp_path / "proxy.log",
        }

    def it_runs_the_image_it_built_for_the_agent(
        run_agent_harness_sandbox, build_agent_image, options, agent
    ):
        run_porting_harness(**options(debug=True))

        build_agent_image.assert_called_once_with(
            agent=agent,
            modify_dockerfile=None,
            build_contexts={INPUT_CONTEXT: options()["input"]},
            debug=True,
        )
        assert run_agent_harness_sandbox.call_args.kwargs["image"] == "an-agent:latest"

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

    def describe_the_input_folder():
        def it_hands_the_input_to_the_build_as_the_named_context(
            run_agent_harness_sandbox, build_agent_image, options, input_directory
        ):
            """COPY reaches it from the Dockerfile the caller extends."""
            run_porting_harness(**options())

            assert build_agent_image.call_args.kwargs["build_contexts"] == {
                INPUT_CONTEXT: input_directory
            }

        def it_mounts_the_input_nowhere(run_agent_harness_sandbox, options):
            """A bind at /input would shadow whatever the build put under it."""
            run_porting_harness(**options())

            assert "input" not in run_agent_harness_sandbox.call_args.kwargs

    def describe_modify_dockerfile():
        def it_hands_the_callers_modifier_to_the_image_build(
            run_agent_harness_sandbox, build_agent_image, options
        ):
            def modify(text):
                return text

            run_porting_harness(**options(modify_dockerfile=modify))

            assert build_agent_image.call_args.kwargs["modify_dockerfile"] is modify

        def it_builds_the_dockerfile_as_it_lies_when_none_is_supplied(
            run_agent_harness_sandbox, build_agent_image, options
        ):
            run_porting_harness(**options())

            assert build_agent_image.call_args.kwargs["modify_dockerfile"] is None

    def it_sends_the_rendered_system_prompt_and_returns_the_output(
        run_agent_harness_sandbox, prompt_class, options
    ):
        """The harness frames the task; the caller's prompt goes in the template's slot."""
        claude_output = run_porting_harness(**options(prompt="Port it.\n"))

        prompt_class.assert_called_once_with(PROMPT_PATH, upstream="Port it.\n")
        assert run_agent_harness_sandbox.call_args.args == ("the rendered prompt",)
        assert claude_output == "container output"
