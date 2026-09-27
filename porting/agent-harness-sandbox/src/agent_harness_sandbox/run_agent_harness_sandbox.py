from collections.abc import Sequence
from pathlib import Path
from tempfile import TemporaryDirectory

from python_on_whales import docker

from .agents.agent import Agent
from .errors import AgentHarnessSandboxError
from .utils.lockdown import lockdown
from .utils.staged_input import staged_input

HOLD = ["sleep", "infinity"]


def run_agent_harness_sandbox(
    prompt: str,
    *,
    agent: Agent,
    image: str,
    input: str | Path,
    outputs: dict[str | Path, str | Path],
    envs: dict[str, str],
    setup: Sequence[str] | None,
    debug: bool,
    home: str | Path,
    transcripts: str | Path,
    proxy_log: str | Path,
    effort: str,
    model: str,
) -> str:
    """Run PROMPT through the agent's own CLI in the sandbox container.

    image is the one to run, built by the caller from build_agent_image's tag:
    either that tag itself or a caller's own layer on top of it. Nothing is
    built here.

    input is the caller's folder. It is copied into the container at /input,
    writable and thrown away when the run ends: the agent can install and scratch
    there, and nothing it writes reaches the caller's folder.

    setup is an argv to run in the container before the agent, or None. It runs
    against that copy with the egress network attached and the proxy env
    withheld, so a dependency install reaches its registry directly; the network
    is detached again before the agent starts, so the agent's reach stays exactly
    agent.allow.

    Every option is required: a default is a value the caller never chose and the
    run record never names.
    """
    command = agent.command(prompt, effort=effort, model=model)

    with (
        lockdown(agent.allow, debug=debug, log_path=proxy_log) as jail,
        TemporaryDirectory() as staged,
        staged_input(input) as input_copy,
    ):
        agent.stage_auth(Path(staged))
        volumes = [(staged, agent.home, "rw")]
        for path, target, mode in [
            (transcripts, agent.transcripts, "rw"),
            (input_copy, "/input", "rw"),
            *((source, target, "rw") for source, target in outputs.items()),
        ]:
            source = Path(path)
            # docker would create a missing source as a root-owned directory.
            if not source.exists():
                raise AgentHarnessSandboxError(f"{source} does not exist")
            volumes.append((str(source.resolve()), str(target), mode))
        print('Running agent sandbox')
        container = docker.run(
            image,
            HOLD,
            detach=True,
            envs=envs,
            volumes=volumes,
            workdir=str(home),
            networks=[jail.network],
            cap_drop=["ALL"],
            security_options=["no-new-privileges"],
        )
        try:
            if setup is not None:
                docker.network.connect(jail.egress, container)
                docker.execute(container, list(setup), envs=envs, workdir=str(home))
                docker.network.disconnect(jail.egress, container)
            return docker.execute(
                container, command, envs={**jail.envs, **envs}, workdir=str(home)
            )
        finally:
            docker.container.remove(container, force=True)
