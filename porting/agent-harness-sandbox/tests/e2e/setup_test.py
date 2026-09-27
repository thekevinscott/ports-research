"""The setup hook: same container as the agent, before it, with the network open.

The install step needs a registry the agent must never reach. Setup fetches
from npm and writes the status where the agent's probe can read it back; the
agent then reports it, and the proxy log shows the fetch never went through
the proxy.
"""

import pytest

from conftest import OUTPUT_TARGET

REGISTRY = "registry.npmjs.org"

SETUP = [
    "sh",
    "-c",
    "node -e \"fetch('https://" + REGISTRY + "/-/ping')"
    ".then(r => process.stdout.write(String(r.status)))\""
    f" > {OUTPUT_TARGET}/setup.txt",
]


@pytest.fixture(scope="module")
def session(sandbox):
    return sandbox({"setup": f"cat {OUTPUT_TARGET}/setup.txt"}, setup=SETUP)


def describe_setup():
    def it_ran_before_the_agent_in_the_same_container(session):
        assert session.report["setup"] == "200"

    def it_reached_the_registry_without_the_proxy(session):
        assert not [line for line in session.denials if REGISTRY in line]
