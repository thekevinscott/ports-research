from measure_transcript.grep_filter import grep_filter


def describe_grep_filter():
    def it_keeps_lines_holding_a_pattern_or_with_v_the_others():
        assert grep_filter(["grep", "sub/"])("gbnf/sub/b.py") is True
        assert grep_filter(["grep", "sub/"])("gbnf/a.py") is False
        keep = grep_filter(["grep", "-v", "-e", "_test", "-e", "GBNF"])
        assert [keep(line) for line in ("a.py", "a_test.py", "GBNF.py")] == [True, False, False]

    def it_returns_none_for_other_stages_and_regex_patterns():
        assert grep_filter(["sort"]) is None
        assert grep_filter(["grep", "-i", "x"]) is None
        assert grep_filter(["grep", "-v", "test.py"]) is None
        assert grep_filter(["grep", "-v"]) is None

    def it_returns_none_when_grep_is_given_a_file():
        assert grep_filter(["grep", "x", "notes"]) is None
        assert grep_filter(["grep", "-e", "x", "notes"]) is None
