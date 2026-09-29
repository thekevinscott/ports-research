from porting_harness.run_porting_harness import INPUT, INPUT_CONTEXT

# The sandbox runs the agent as node, and a root-owned tree would leave it unable
# to install under the source it was given.
COPY_REFERENCE = f"COPY --from={INPUT_CONTEXT} --chown=node:node . {INPUT}/\n"


def copy_reference_into_image(agent_dockerfile: str) -> str:
    """Append the instruction that puts the assembled reference in the image.

    The reference has to be in the image rather than mounted over it, because
    installing its dependencies is a build step and a bind at INPUT would hide
    whatever the build wrote there.
    """
    return agent_dockerfile + COPY_REFERENCE
