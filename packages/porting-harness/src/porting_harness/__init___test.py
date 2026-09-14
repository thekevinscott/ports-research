from . import PROMPT_PATH, __all__, run_porting_harness


def describe_porting_harness():
    def it_publishes_the_runner_and_the_prompt_path():
        assert __all__ == ["PROMPT_PATH", "run_porting_harness"]

    def it_binds_the_runner():
        assert callable(run_porting_harness)

    def it_binds_the_prompt_path():
        assert PROMPT_PATH.name == "prompt.txt"
