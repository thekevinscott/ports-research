from pathlib import Path
from tempfile import TemporaryDirectory

from python_on_whales import docker

from .agents import Agent
from .config import (
    BASE_DOCKERFILE,
    BASE_IMAGE,
    SANDBOX_DIR,
)
from .errors import AgentHarnessSandboxError
from .utils.lockdown import lockdown


def run_agent_harness_sandbox(
    prompt: str,
    *,
    agent: Agent,
    inputs: dict[str | Path, str | Path],
    outputs: dict[str | Path, str | Path],
    envs: dict[str, str],
    debug: bool,
    home: str | Path,
    transcripts: str | Path,
    proxy_log: str | Path,
    effort: str,
    model: str,
) -> str:
    """Run PROMPT through the agent's own CLI in the sandbox container.

    Every option is required: a default is a value the caller never chose and the
    run record never names.
    """
    progress = "tty" if debug else False
    print('Building Docker containers')
    docker.build(SANDBOX_DIR, tags=BASE_IMAGE, file=BASE_DOCKERFILE, progress=progress)
    docker.build(SANDBOX_DIR, tags=agent.image, file=agent.dockerfile, progress=progress)
    print('Built Docker containers')

    command = agent.command(prompt, effort=effort, model=model)

    with (
        lockdown(agent.allow, debug=debug, log_path=proxy_log) as jail,
        TemporaryDirectory() as staged,
    ):
        agent.stage_auth(Path(staged))
        volumes = [(staged, agent.home, "rw")]
        for path, target, mode in [
            (transcripts, agent.transcripts, "rw"),
            *((source, target, "ro") for source, target in inputs.items()),
            *((source, target, "rw") for source, target in outputs.items()),
        ]:
            source = Path(path)
            # docker would create a missing source as a root-owned directory.
            if not source.exists():
                raise AgentHarnessSandboxError(f"{source} does not exist")
            volumes.append((str(source.resolve()), str(target), mode))
        print('Running agent sandbox')
        return docker.run(
            agent.image,
            command,
            envs={**jail.envs, **envs},
            volumes=volumes,
            remove=True,
            workdir=str(home),
            networks=[jail.network],
            cap_drop=["ALL"],
            security_options=["no-new-privileges"],
        )
