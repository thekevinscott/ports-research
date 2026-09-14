from . import Lockdown, __all__, lockdown


def describe_utils():
    def it_publishes_the_lockdown_pair():
        assert __all__ == ["Lockdown", "lockdown"]

    def it_binds_the_context_manager():
        assert callable(lockdown)

    def it_binds_the_handle_type():
        assert isinstance(Lockdown, type)
