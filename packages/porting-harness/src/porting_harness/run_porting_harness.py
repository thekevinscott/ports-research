from pathlib import Path

from agent_harness_sandbox.agents.agent import Agent
from agent_harness_sandbox.build_agent_image import build_agent_image
from agent_harness_sandbox.run_agent_harness_sandbox import run_agent_harness_sandbox

from .render_prompt import render_prompt

DOCKER_HOMEBASE = Path("/workspace")
PROMPT_PATH = Path(__file__).parent / "prompt.txt"


def run_porting_harness(
    *,
    agent: Agent,
    reference_implementation: Path,
    target_language: str,
    output_directory: Path,
    debug: bool,
    effort: str,
    model: str,
    transcripts: Path,
    proxy_log: Path,
) -> str:
    """Port reference_implementation into target_language, into output_directory.

    The prompt is this harness's own: PROMPT_PATH rendered for target_language.
    A caller says what it wants ported and in which direction, never how to
    phrase it — one wording across every arm is what makes the arms comparable.

    reference_implementation holds the source tree under `source/` and, when a
    suite was selected, the test suites under `tests/`; the two mount read-only
    and separately, and tests/ is not mounted at all when it is absent.
    output_directory is bound writable and is the port, as the agent leaves it.
    transcripts is a host directory the CLI writes the session jsonl into and
    proxy_log a host file the sidecar's log is drained to at teardown.

    Nothing has a default. A run that banks no transcript, no denial log or no
    model name produces evidence nobody can attribute afterwards.
    """
    output_directory.mkdir(parents=True, exist_ok=True)
    return run_agent_harness_sandbox(
        render_prompt(PROMPT_PATH, target_language),
        agent=agent,
        image=build_agent_image(agent=agent, debug=debug),
        inputs={
            reference_implementation
            / "source": DOCKER_HOMEBASE / "reference_implementation",
            **(
                {reference_implementation / "tests": DOCKER_HOMEBASE / "tests"}
                if (reference_implementation / "tests").is_dir()
                else {}
            ),
        },
        outputs={output_directory: DOCKER_HOMEBASE / "ported_implementation"},
        envs={},
        debug=debug,
        home=DOCKER_HOMEBASE,
        effort=effort,
        model=model,
        transcripts=transcripts,
        proxy_log=proxy_log,
    )
