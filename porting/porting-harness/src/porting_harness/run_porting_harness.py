from pathlib import Path

from agent_harness_sandbox.agents.agent import Agent
from agent_harness_sandbox.build_agent_image import build_agent_image
from agent_harness_sandbox.run_agent_harness_sandbox import run_agent_harness_sandbox

DOCKER_HOMEBASE = Path("/workspace")


def run_porting_harness(
    *,
    agent: Agent,
    prompt: str,
    reference: Path,
    output_directory: Path,
    debug: bool,
    effort: str,
    model: str,
    transcripts: Path,
    proxy_log: Path,
) -> str:
    """Run prompt against reference in the sandbox, collecting the port in output_directory.

    reference is one folder, mounted read-only at /input. The caller laid it
    out and the caller's prompt describes it: what is the source, what is a
    suite, what to port to. The harness adds no words. output_directory is
    bound writable and is the port, as the agent leaves it. transcripts is a
    host directory the CLI writes the session jsonl into and proxy_log a host
    file the sidecar's log is drained to at teardown.

    Nothing has a default. A run that banks no transcript, no denial log or no
    model name produces evidence nobody can attribute afterwards.
    """
    output_directory.mkdir(parents=True, exist_ok=True)
    return run_agent_harness_sandbox(
        prompt,
        agent=agent,
        image=build_agent_image(agent=agent, debug=debug),
        input_folder=reference,
        outputs={output_directory: DOCKER_HOMEBASE / "ported_implementation"},
        envs={},
        debug=debug,
        home=DOCKER_HOMEBASE,
        effort=effort,
        model=model,
        transcripts=transcripts,
        proxy_log=proxy_log,
    )
