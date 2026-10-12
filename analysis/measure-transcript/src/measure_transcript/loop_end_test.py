from measure_transcript.loop_end import loop_end


def describe_loop_end():
    def it_spans_the_body_between_do_and_done():
        tokens = ["for", "f", "in", "a", ";", "do", "cat", "$f", ";", "done", "|", "head"]
        assert loop_end(tokens, 4) == (6, 9)

    def it_skips_a_nested_loop_and_newlines():
        tokens = ["for", "a", "in", "1", ";\n", "do", "for", "b", "in", "x", ";", "do", "echo", ";", "done", ";", "done"]
        assert loop_end(tokens, 4) == (6, 16)

    def it_returns_none_without_do_or_done():
        assert loop_end(["for", "f", "in", "a", ";", "cat", "$f"], 4) is None
        assert loop_end(["for", "f", "in", "a", ";", "do", "cat", "$f"], 4) is None
        assert loop_end(["echo", "do", ";", "done"], 2) is None
