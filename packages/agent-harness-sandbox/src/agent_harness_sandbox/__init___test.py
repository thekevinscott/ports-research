from . import (
    Agent,
    AgentHarnessSandboxError,
    ClaudeAgent,
    Lockdown,
    PiAgent,
    __all__,
    lockdown,
    run_agent_harness_sandbox,
)


def describe_agent_harness_sandbox():
    def it_publishes_the_runner_the_agents_and_the_lockdown():
        assert __all__ == [
            "Agent",
            "AgentHarnessSandboxError",
            "ClaudeAgent",
            "Lockdown",
            "PiAgent",
            "lockdown",
            "run_agent_harness_sandbox",
        ]

    def it_binds_the_runner():
        assert callable(run_agent_harness_sandbox)

    def it_binds_the_lockdown():
        assert callable(lockdown)
        assert isinstance(Lockdown, type)

    def it_binds_every_agent():
        assert isinstance(Agent, type)
        assert isinstance(ClaudeAgent, type)
        assert isinstance(PiAgent, type)

    def it_binds_the_error_as_an_exception():
        assert issubclass(AgentHarnessSandboxError, Exception)
