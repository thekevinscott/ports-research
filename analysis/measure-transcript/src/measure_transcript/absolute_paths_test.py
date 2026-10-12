from measure_transcript.absolute_paths import absolute_paths


def describe_absolute_paths():
    def it_finds_absolute_paths_in_text():
        text = "sys.path.insert(0, '/input/python')\nimport GBNF from '/target/src/index.ts';"
        assert absolute_paths(text) == ["/input/python", "/target/src/index.ts"]

    def it_ignores_urls_relative_paths_and_division():
        assert absolute_paths("see https://x.org/a and ./b/c and a/b and x / y") == []
