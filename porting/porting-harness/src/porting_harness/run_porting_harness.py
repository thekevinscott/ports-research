from pathlib import Path

from agent_harness_sandbox.agents.agent import Agent
from agent_harness_sandbox.build_agent_image import build_agent_image
from agent_harness_sandbox.run_agent_harness_sandbox import run_agent_harness_sandbox

from .render_prompt import render_prompt

DOCKER_HOMEBASE = Path("/workspace")
TARGET = Path("/target")
PROMPT_PATH = Path(__file__).parent / "prompt.txt"


def run_porting_harness(
    *,
    agent: Agent,
    prompt: str,
    input: Path,
    output_directory: Path,
    debug: bool,
    effort: str,
    model: str,
    transcripts: Path,
    proxy_log: Path,
) -> str:
    """Run prompt against input in the sandbox, collecting the port in output_directory.

    input is one folder, mounted read-only at /input. prompt is the caller's
    upstream prompt: the caller laid the folder out and is the only one who can
    say what is the source, what is a suite, what to port to. It is appended to
    the harness's own system prompt, which frames the task and names the two
    container paths: the reference at /input, the port at /target.
    output_directory is bound writable at /target and is the port, as the agent
    leaves it. transcripts is a host directory the CLI writes the session jsonl
    into and proxy_log a host file the sidecar's log is drained to at teardown.

    Nothing has a default. A run that banks no transcript, no denial log or no
    model name produces evidence nobody can attribute afterwards.
    """
    output_directory.mkdir(parents=True, exist_ok=True)
    return run_agent_harness_sandbox(
        render_prompt(PROMPT_PATH, prompt),
        agent=agent,
        image=build_agent_image(agent=agent, debug=debug),
        input=input,
        outputs={output_directory: TARGET},
        envs={},
        setup=None,
        debug=debug,
        home=DOCKER_HOMEBASE,
        effort=effort,
        model=model,
        transcripts=transcripts,
        proxy_log=proxy_log,
    )
