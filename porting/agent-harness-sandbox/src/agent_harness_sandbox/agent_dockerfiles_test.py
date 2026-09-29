"""The shipped agent Dockerfiles, as text.

The stage structure is what the later slices hang off: stage 1 gets the network
and installs, the run stage inherits only what it is handed. Flattening these
back to one stage would leave every other test green while putting the installs
back into the image the agent runs in, so the structure is asserted directly.
"""

from agent_harness_sandbox.agents.ClaudeAgent import ClaudeAgent
from agent_harness_sandbox.agents.PiAgent import PiAgent

AGENTS = (ClaudeAgent, PiAgent)
SETUP_STAGE = "dependencies"
STAGED_PATH = "/input"


def shipped() -> dict[str, str]:
    return {agent.__name__: agent.dockerfile.read_text() for agent in AGENTS}


def run_stage(text: str) -> str:
    return text.split(f"AS {SETUP_STAGE}")[1].split("\nFROM ")[1]


def describe_the_shipped_agent_dockerfiles():
    def it_names_a_first_stage_for_the_run_stage_to_copy_from():
        for name, text in shipped().items():
            assert f"AS {SETUP_STAGE}" in text, name

    def it_ends_the_first_stage_as_the_user_the_agent_runs_as():
        """A caller appending an install there must not produce root-owned files."""
        for name, text in shipped().items():
            setup = text.split(f"AS {SETUP_STAGE}")[1].split("\nFROM ")[0]
            assert setup.rstrip().endswith("USER node"), name

    def it_carries_the_staged_path_into_the_run_stage():
        for name, text in shipped().items():
            assert f"COPY --from={SETUP_STAGE}" in run_stage(text), name
            assert f"{STAGED_PATH} {STAGED_PATH}" in run_stage(text), name

    def it_leaves_the_agents_own_cli_in_the_run_stage():
        """Stage 1 is for the port's dependencies; the CLI belongs where it runs."""
        for name, text in shipped().items():
            assert "npm install -g" in run_stage(text), name
