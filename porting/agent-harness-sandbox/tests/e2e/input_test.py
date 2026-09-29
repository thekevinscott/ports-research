"""EVERY TEST IN THIS FILE INVOKES CLAUDE FOR REAL AND IS BILLED.

The input tree reaches the container through the image rather than a mount, so
the two claims worth a live run are that the agent can find and change it, and
that nothing it does there reaches the folder the caller handed over.
"""

import pytest

from conftest import PROBE_TARGET, SCRIPT

SCRATCH = "scratch"

PROBES = {
    "listing": f"ls {PROBE_TARGET}",
    "write": f"touch {PROBE_TARGET}/{SCRATCH} 2>/dev/null && echo writable || echo readonly",
}


@pytest.fixture(scope="module")
def session(sandbox):
    return sandbox(PROBES)


def describe_the_input_the_image_was_built_with():
    def it_is_there_for_the_agent_to_read(session):
        """No bind sits over it, so what the build copied in is what the agent sees."""
        assert SCRIPT in session.report["listing"].split()

    def it_is_writable_by_the_agent(session):
        """Installing the port's dependencies happens under it, so root-owned is no good."""
        assert session.report["write"] == "writable"

    def it_keeps_what_the_container_wrote_off_the_host(session):
        """The container is ephemeral, which is what the discarded mount copy used to do."""
        assert not (session.probe / SCRATCH).exists()
