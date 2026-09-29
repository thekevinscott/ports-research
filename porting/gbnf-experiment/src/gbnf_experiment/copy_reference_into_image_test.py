from porting_harness.run_porting_harness import INPUT, INPUT_CONTEXT

from gbnf_experiment.copy_reference_into_image import copy_reference_into_image

AGENT_DOCKERFILE = "FROM agent-harness-sandbox-base:latest\nUSER node\n"


def describe_copy_reference_into_image():
    def it_keeps_the_agent_layer_it_was_given():
        assert copy_reference_into_image(AGENT_DOCKERFILE).startswith(AGENT_DOCKERFILE)

    def it_copies_the_input_context_to_the_path_the_prompt_names():
        assert f"COPY --from={INPUT_CONTEXT} " in copy_reference_into_image(AGENT_DOCKERFILE)
        assert copy_reference_into_image(AGENT_DOCKERFILE).rstrip().endswith(f". {INPUT}/")

    def it_hands_the_tree_to_the_user_the_agent_runs_as():
        """Root-owned files would leave the agent unable to install under them."""
        assert "--chown=node:node" in copy_reference_into_image(AGENT_DOCKERFILE)

    def it_adds_one_instruction_and_nothing_else():
        added = copy_reference_into_image(AGENT_DOCKERFILE)[len(AGENT_DOCKERFILE) :]
        assert added.splitlines() == [
            f"COPY --from={INPUT_CONTEXT} --chown=node:node . {INPUT}/"
        ]
