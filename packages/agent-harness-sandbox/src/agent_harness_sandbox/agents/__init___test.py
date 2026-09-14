from . import Agent, ClaudeAgent, PiAgent, __all__


def describe_agents():
    def it_publishes_the_protocol_and_both_implementations():
        assert __all__ == ["Agent", "ClaudeAgent", "PiAgent"]

    def it_binds_every_published_name():
        assert isinstance(Agent, type)
        assert isinstance(ClaudeAgent, type)
        assert isinstance(PiAgent, type)
