from collections.abc import Callable
from pathlib import Path

from agent_harness_sandbox.agents.agent import Agent
from agent_harness_sandbox.build_agent_image import build_agent_image
from agent_harness_sandbox.run_agent_harness_sandbox import run_agent_harness_sandbox

from .prompt import Prompt

DOCKER_HOMEBASE = Path("/workspace")
INPUT = Path("/input")
TARGET = Path("/target")
# The build context the input folder arrives as, for a caller's COPY --from.
INPUT_CONTEXT = "input"
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

    input reaches the container through the image, not a mount: it is handed to
    the build as the `INPUT_CONTEXT` context, and `modify_dockerfile` is where a
    caller copies it to `INPUT`. A bind at `INPUT` would shadow whatever the
    build put under it, so there is none.
    """
    output_directory.mkdir(parents=True, exist_ok=True)
    return run_agent_harness_sandbox(
        str(Prompt(PROMPT_PATH, upstream=prompt)),
        agent=agent,
        image=build_agent_image(
            agent=agent,
            modify_dockerfile=modify_dockerfile,
            build_contexts={INPUT_CONTEXT: input},
            debug=debug,
        ),
        outputs={output_directory: TARGET},
        envs={},
        debug=debug,
        home=DOCKER_HOMEBASE,
        effort=effort,
        model=model,
        transcripts=transcripts,
        proxy_log=proxy_log,
    )
