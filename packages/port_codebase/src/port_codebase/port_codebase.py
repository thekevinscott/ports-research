from pathlib import Path

from botbox import Agent, Botbox, RunResult

from prompt import Prompt

PROMPT_PATH = Path(__file__).parent / "prompts" / "prompt.txt"
# Each must start FROM the image it is keyed by: botbox layers it on the agent's own image.
DOCKERFILES = {
    "botbox-claude:latest": Path(__file__).parent / "Dockerfile.claude",
    "botbox-codex:latest": Path(__file__).parent / "Dockerfile.codex",
}


async def port_codebase(
    *, agent: Agent, prompt: str, source: Path, output: Path, artifacts: Path, memory: str
) -> RunResult:
    """Run the agent on `prompt` with `source` at /input (ro) and `output` at /target (rw).

    The prompt carries both Dockerfiles as they are on disk at call time, so the agent
    reads the image it is actually in.
    """
    if not source.exists():
        raise FileNotFoundError(f"source {source} does not exist")
    dockerfile = DOCKERFILES[agent.image]
    output.mkdir(parents=True, exist_ok=True)
    rendered = Prompt(
        PROMPT_PATH,
        agent_dockerfile=agent.dockerfile.read_text().rstrip("\n"),
        dockerfile=dockerfile.read_text().rstrip("\n"),
        upstream=prompt,
    )
    async with Botbox(agent, dockerfile=dockerfile, memory=memory) as box:
        return await box.run(
            agent.command(str(rendered)),
            mounts=((source, "/input", "ro"), (output, "/target", "rw")),
            workdir="/target",
            output=artifacts,
        )
