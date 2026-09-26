"""The posture a real run applies to the container it starts.

The sandbox runs claude with `--dangerously-skip-permissions`, so the container
walls are the entire permission boundary. Every probe reads a file the kernel
already publishes; nothing runs an exploit. Only what this package decides is
asserted — Docker's stock defaults and the base image's own move without it.
"""

import pytest

EMPTY_CAPABILITY_MASK = "0" * 16

PROBES = {
    "uid": "id -u",
    "bounding_set": "grep ^CapBnd: /proc/self/status | cut -f2",
    "no_new_privs": "grep ^NoNewPrivs: /proc/self/status | cut -f2",
    "setuid_binaries": "find / -xdev -perm /6000 -type f 2>/dev/null | sort",
    "input_write": "touch /workspace/probe/scratch 2>/dev/null && echo writable || echo readonly",
}


@pytest.fixture(scope="module")
def posture(sandbox) -> dict[str, str]:
    return sandbox(PROBES).report


def describe_the_sandbox_container():
    def it_runs_as_the_unprivileged_node_user(posture):
        assert posture["uid"] == "1000"

    def it_drops_the_capability_bounding_set(posture):
        """The ceiling that would apply if a process in here ever reached uid 0."""
        assert posture["bounding_set"] == EMPTY_CAPABILITY_MASK

    def it_forbids_privilege_escalation_through_setuid(posture):
        """The other half: no_new_privs makes a setuid execve a no-op."""
        assert posture["no_new_privs"] == "1"

    def it_ships_no_setuid_or_setgid_binaries(posture):
        """The half that survives a caller starting the image without the run flags."""
        assert posture["setuid_binaries"] == ""

    def it_cannot_write_to_a_mounted_input(posture):
        """The caller's tree is the reference the run is judged against, so the run cannot edit it."""
        assert posture["input_write"] == "readonly"
