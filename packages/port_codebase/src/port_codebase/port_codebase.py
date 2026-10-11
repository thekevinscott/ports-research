from pathlib import Path

from botbox import Agent, Botbox, RunResult

from prompt import Prompt

PROMPT_PATH = Path(__file__).parent / "prompts" / "prompt.txt"
DOCKERFILE = Path(__file__).parent / "Dockerfile"


def port_codebase(*, agent: Agent, prompt: str, source: Path, output: Path) -> RunResult:
    """Run the agent on `prompt` with `source` at /input (ro) and `output` at /target (rw)."""
    if not source.exists():
        raise FileNotFoundError(f"source {source} does not exist")
    output.mkdir(parents=True, exist_ok=True)
    return Botbox(agent, dockerfile=DOCKERFILE).run(
        agent.command(str(Prompt(PROMPT_PATH, upstream=prompt))),
        mounts=((source, "/input", "ro"), (output, "/target", "rw")),
        workdir="/target",
    )
