import pytest

from contamination_probe.locate_name_offset import locate_name_offset


def describe_locate_name_offset():
    def it_finds_a_name_on_the_first_line():
        assert locate_name_offset("class Graph:\n    pass\n", 1, "Graph") == 6

    def it_finds_a_name_on_a_later_line():
        text = "from x import y\n\nclass Graph:\n    pass\n"
        assert locate_name_offset(text, 3, "Graph") == len("from x import y\n\nclass ")

    def it_does_not_match_a_name_that_is_only_a_substring_of_a_longer_identifier():
        with pytest.raises(ValueError):
            locate_name_offset("class GraphNode:\n    pass\n", 1, "Graph")

    def it_matches_the_full_identifier_it_is_a_substring_of():
        text = "class GraphNode:\n    pass\n"
        offset = locate_name_offset(text, 1, "GraphNode")
        assert text[offset : offset + len("GraphNode")] == "GraphNode"

    def it_raises_when_the_name_is_not_on_that_line():
        with pytest.raises(ValueError):
            locate_name_offset("class Graph:\n    pass\n", 1, "Missing")
