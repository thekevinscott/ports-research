import re
from random import Random

from contamination_probe.generate_synthetic_name import generate_synthetic_name


def describe_generate_synthetic_name():
    def it_is_deterministic_for_a_given_random_state(monkeypatch):
        assert generate_synthetic_name("Graph", Random(0)) == generate_synthetic_name(
            "Graph", Random(0)
        )

    def it_varies_with_random_state(monkeypatch):
        assert generate_synthetic_name("Graph", Random(0)) != generate_synthetic_name(
            "Graph", Random(1)
        )

    def it_matches_pascal_case_for_a_pascal_case_original():
        name = generate_synthetic_name("GraphNode", Random(0))
        assert re.fullmatch(r"[A-Z][a-zA-Z]*", name)

    def it_matches_screaming_snake_case_for_a_screaming_snake_case_original():
        name = generate_synthetic_name("ROOT_NODE", Random(0))
        assert re.fullmatch(r"[A-Z]+(_[A-Z]+)+", name)

    def it_matches_snake_case_for_a_snake_case_original():
        name = generate_synthetic_name("is_point_in_range", Random(0))
        assert re.fullmatch(r"[a-z]+(_[a-z]+)+", name)

    def it_never_returns_the_original_name():
        for seed in range(20):
            assert generate_synthetic_name("Graph", Random(seed)) != "Graph"
