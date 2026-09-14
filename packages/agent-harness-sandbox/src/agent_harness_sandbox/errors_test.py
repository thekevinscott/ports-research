import pytest

from agent_harness_sandbox.errors import AgentHarnessSandboxError


def describe_agent_harness_sandbox_error():
    def it_is_an_exception():
        assert issubclass(AgentHarnessSandboxError, Exception)

    def it_carries_its_message():
        assert str(AgentHarnessSandboxError("no creds")) == "no creds"

    def it_can_be_raised_and_caught():
        with pytest.raises(AgentHarnessSandboxError, match="boom"):
            raise AgentHarnessSandboxError("boom")
