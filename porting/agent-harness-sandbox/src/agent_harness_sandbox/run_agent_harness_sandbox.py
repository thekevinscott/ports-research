from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory

from python_on_whales import docker

from .agents.agent import Agent
from .errors import AgentHarnessSandboxError
from .utils.lockdown import lockdown


def run_agent_harness_sandbox(
    prompt: str,
    *,
    agent: Agent,
    image: str,
    input: str | Path,
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

    image is the one to run, built by the caller from build_agent_image's tag:
    either that tag itself or a caller's own layer on top of it. Nothing is
    built here.

    input is the caller's folder. It is copied into the container at /input,
    writable and thrown away when the run ends: the agent can install and scratch
    there, and nothing it writes reaches the caller's folder.

    Every option is required: a default is a value the caller never chose and the
    run record never names.
    """
    command = agent.command(prompt, effort=effort, model=model)
    caller_input = Path(input)
    if not caller_input.exists():
        raise AgentHarnessSandboxError(f"{caller_input} does not exist")
    if not caller_input.is_dir():
        raise AgentHarnessSandboxError(f"{caller_input} is not a directory")

    with (
        lockdown(agent.allow, debug=debug, log_path=proxy_log) as jail,
        TemporaryDirectory() as staged,
        TemporaryDirectory() as staging,
    ):
        agent.stage_auth(Path(staged))
        staged_input = Path(staging) / "input"
        copytree(caller_input, staged_input, symlinks=True)
        volumes = [(staged, agent.home, "rw")]
        for path, target, mode in [
            (transcripts, agent.transcripts, "rw"),
            (staged_input, "/input", "rw"),
            *((source, target, "rw") for source, target in outputs.items()),
        ]:
            source = Path(path)
            # docker would create a missing source as a root-owned directory.
            if not source.exists():
                raise AgentHarnessSandboxError(f"{source} does not exist")
            volumes.append((str(source.resolve()), str(target), mode))
        print('Running agent sandbox')
        return docker.run(
            image,
            command,
            envs={**jail.envs, **envs},
            volumes=volumes,
            remove=True,
            workdir=str(home),
            networks=[jail.network],
            cap_drop=["ALL"],
            security_options=["no-new-privileges"],
        )
