"""The shipped Dockerfile, as text.

The stage structure is what the later slices hang off: stage 1 gets the network
and installs, the run stage inherits only what it is handed. Flattening these
back to one stage would leave every other test green while putting the installs
back into the image the agent runs in, so the structure is asserted directly.
"""

from agent_harness_sandbox.agents.ClaudeAgent import ClaudeAgent
from agent_harness_sandbox.agents.PiAgent import PiAgent
from agent_harness_sandbox.config import DOCKERFILE

AGENTS = (ClaudeAgent, PiAgent)
SETUP_STAGE = "dependencies"
STAGED_PATH = "/input"
RUN_STAGE = "FROM ${AGENT}"


def stages() -> dict[str, str]:
    """Each stage's body, keyed by its FROM line."""
    _, *blocks = DOCKERFILE.read_text().split("\nFROM ")
    return {f"FROM {block.split(chr(10))[0]}": block for block in blocks}


def named(name: str) -> str:
    [body] = [body for line, body in stages().items() if line.endswith(f" AS {name}")]
    return body


def describe_the_shipped_dockerfile():
    def it_names_a_stage_for_every_agent():
        for agent in AGENTS:
            assert named(agent.stage)

    def it_ends_the_first_stage_as_the_user_the_agent_runs_as():
        """A caller installing there must not produce root-owned files."""
        assert named(SETUP_STAGE).rstrip().endswith("USER node")

    def it_runs_the_stage_the_agent_argument_names():
        assert list(stages())[-1] == RUN_STAGE

    def it_carries_the_staged_path_into_the_run_stage():
        run_stage = stages()[RUN_STAGE]
        assert f"COPY --from={SETUP_STAGE}" in run_stage
        assert f"{STAGED_PATH} {STAGED_PATH}" in run_stage

    def it_leaves_the_agents_own_cli_out_of_the_first_stage():
        """Stage 1 is for the port's dependencies; the CLI belongs where it runs."""
        assert "npm install -g" not in named(SETUP_STAGE)
        for agent in AGENTS:
            assert "npm install -g" in named(agent.stage), agent.__name__
