from pathlib import Path

from agent_harness_sandbox.agents.agent import Agent
from agent_harness_sandbox.run_agent_harness_sandbox import run_agent_harness_sandbox

from .render_prompt import render_prompt

DOCKER_HOMEBASE = Path("/workspace")
PROMPT_PATH = Path(__file__).parent / "prompt.txt"


def run_porting_harness(
    *,
    agent: Agent,
    image: str,
    target_language: str,
    output_directory: Path,
    debug: bool,
    effort: str,
    model: str,
    transcripts: Path,
    proxy_log: Path,
) -> str:
    """Port the reference baked into image into target_language, into output_directory.

    The prompt is this harness's own: PROMPT_PATH rendered for target_language.
    A caller says what it wants ported and in which direction, never how to
    phrase it — one wording across every arm is what makes the arms comparable.

    image is a layer on the agent's sandbox image carrying the reference at
    /workspace/reference_implementation and, when the caller chose one, a
    suite at /workspace/tests. Nothing is mounted in: what the agent can read
    is fixed when the image is built. output_directory is bound writable and
    is the port, as the agent leaves it. transcripts is a host directory the
    CLI writes the session jsonl into and proxy_log a host file the sidecar's
    log is drained to at teardown.

    Nothing has a default. A run that banks no transcript, no denial log or no
    model name produces evidence nobody can attribute afterwards.
    """
    output_directory.mkdir(parents=True, exist_ok=True)
    return run_agent_harness_sandbox(
        render_prompt(PROMPT_PATH, target_language),
        agent=agent,
        image=image,
        inputs={},
        outputs={output_directory: DOCKER_HOMEBASE / "ported_implementation"},
        envs={},
        debug=debug,
        home=DOCKER_HOMEBASE,
        effort=effort,
        model=model,
        transcripts=transcripts,
        proxy_log=proxy_log,
    )
