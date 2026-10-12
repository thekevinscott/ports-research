from measure_transcript.find_output import find_output

FILES = {
    "/input/python/gbnf/__init__.py",
    "/input/python/gbnf/GBNF.py",
    "/input/python/gbnf/graph_test.py",
    "/input/python/gbnf/sub/b.py",
    "/input/python/tests/c_test.py",
    "/input/python/README.md",
}


def describe_find_output():
    def it_prints_the_listed_files_a_sorted_find_matches_under_its_start_directories():
        segments = [["find", "gbnf", "-name", "*.py", "!", "-name", "*_test.py"], ["sort"]]
        assert find_output(segments, "/input/python", FILES) == ["gbnf/GBNF.py", "gbnf/__init__.py", "gbnf/sub/b.py"]

    def it_applies_type_path_and_not():
        segments = [["find", ".", "-type", "f", "-name", "*.py", "-not", "-path", "*/sub/*"], ["sort"]]
        assert find_output(segments, "/input/python/gbnf", FILES) == ["./GBNF.py", "./__init__.py", "./graph_test.py"]

    def it_sorts_across_start_directories():
        assert find_output([["find", "tests", "gbnf/sub", "-name", "*.py"], ["sort"]], "/input/python", FILES) == ["gbnf/sub/b.py", "tests/c_test.py"]

    def it_filters_through_grep_stages_with_plain_patterns():
        segments = [["find", "gbnf", "-name", "*.py"], ["grep", "-v", "_test"], ["sort"], ["grep", "-v", "-e", "GBNF", "-e", "nothing"]]
        assert find_output(segments, "/input/python", FILES) == ["gbnf/__init__.py", "gbnf/sub/b.py"]
        assert find_output([["find", "gbnf"], ["sort"], ["grep", "sub/"]], "/input/python", FILES) == ["gbnf/sub/b.py"]

    def it_cannot_tell_the_order_of_an_unsorted_find():
        assert find_output([["find", "gbnf", "-name", "*.py"]], "/input/python", FILES) is None
        assert find_output([["find", "gbnf"], ["grep", "-v", "_test"]], "/input/python", FILES) is None

    def it_cannot_tell_outside_the_reference_or_past_the_supported_tests():
        assert find_output([["find", "/target", "-name", "*.py"], ["sort"]], "/", FILES) is None
        assert find_output([["find", ".", "-size", "+0"], ["sort"]], "/input/python", FILES) is None
        assert find_output([["find", ".", "-type", "d"], ["sort"]], "/input/python", FILES) is None
        assert find_output([["find", "."], ["grep", "-v", "test.py"], ["sort"]], "/input/python", FILES) is None
        assert find_output([["find", "."], ["grep", "-i", "test"], ["sort"]], "/input/python", FILES) is None
        assert find_output([["find", "."], ["sort", "-r"]], "/input/python", FILES) is None
        assert find_output([["ls", "."], ["sort"]], "/input/python", FILES) is None
