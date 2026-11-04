from pathlib import Path

from adocker import Container, Volume
from botbox import Agent, Botbox, RunResult

from prompt import Prompt

PROMPT_PATH = Path(__file__).parent / "prompts" / "prompt.txt"
DOCKERFILE = Path(__file__).parent / "Dockerfile"
CONTINUE_PROMPT = "Continue the port where you left off."


async def port_codebase(
    *,
    agent: Agent,
    prompt: str,
    source: Path,
    output: Path,
    artifacts: Path,
    memory: str,
    container: str,
    resume: bool,
) -> RunResult:
    """Run the agent on `prompt` with `source` at /input (ro) and `output` at /target (rw).

    The prompt carries both Dockerfiles as they are on disk at call time, so the agent
    reads the image it is actually in.

    The agent container is kept as `container` until the agent exits 0. With `resume`, the
    kept container is restarted and the agent continues its last session.
    """
    if not source.exists():
        raise FileNotFoundError(f"source {source} does not exist")
    output.mkdir(parents=True, exist_ok=True)
    mounts = ((source, "/input", "ro"), (output, "/target", "rw"))
    async with Botbox(agent, dockerfile=DOCKERFILE, memory=memory) as box:
        if resume:
            result = await box.restart(
                container,
                agent.command(CONTINUE_PROMPT, resume=True),
                mounts=mounts,
                workdir="/target",
                output=artifacts,
            )
        else:
            rendered = Prompt(
                PROMPT_PATH,
                agent_dockerfile=agent.dockerfile.read_text().rstrip("\n"),
                dockerfile=DOCKERFILE.read_text().rstrip("\n"),
                upstream=prompt,
            )
            result = await box.run(
                agent.command(str(rendered)),
                mounts=mounts,
                workdir="/target",
                output=artifacts,
                keep=container,
            )
    if result.exit_code == 0:
        await remove_kept(container)
    return result


async def remove_kept(name: str) -> None:
    """Remove the kept container and the run volume botbox leaves with it."""
    kept = Container(name)
    token = (await kept.inspect())["Config"]["Labels"]["botbox.run"]
    await kept.remove()
    await Volume(f"botbox-run-{token}").remove()
