from collections.abc import Callable
from pathlib import Path

from agent_harness_sandbox.agents.agent import Agent
from agent_harness_sandbox.build_agent_image import build_agent_image
from agent_harness_sandbox.run_agent_harness_sandbox import run_agent_harness_sandbox

from .prompt import Prompt

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
    modify_dockerfile: Callable[[str], str] | None = None,
) -> str:
    """Run prompt against input in the sandbox, collecting the port in output_directory.
    """
    output_directory.mkdir(parents=True, exist_ok=True)
    return run_agent_harness_sandbox(
        str(Prompt(PROMPT_PATH, upstream=prompt)),
        agent=agent,
        image=build_agent_image(agent=agent, modify_dockerfile=modify_dockerfile, debug=debug),
        input=input,
        outputs={output_directory: TARGET},
        envs={},
        debug=debug,
        home=DOCKER_HOMEBASE,
        effort=effort,
        model=model,
        transcripts=transcripts,
        proxy_log=proxy_log,
    )
