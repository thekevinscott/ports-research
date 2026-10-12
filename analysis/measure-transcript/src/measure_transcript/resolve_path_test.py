from measure_transcript.resolve_path import resolve_path


def describe_resolve_path():
    def it_joins_a_relative_path_to_the_cwd():
        assert resolve_path("src/a.ts", "/target") == "/target/src/a.ts"

    def it_normalizes_an_absolute_path():
        assert resolve_path("/input/python/../javascript/./src", "/target") == "/input/javascript/src"

    def it_resolves_dot_to_the_cwd():
        assert resolve_path(".", "/input/python") == "/input/python"
