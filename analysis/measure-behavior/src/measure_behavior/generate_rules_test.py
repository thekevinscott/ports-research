import random

from measure_behavior.generate_rules import generate_rules


def references(node):
    if node[0] == "ref":
        yield node[1]
    if node[0] in ("seq", "alt"):
        for child in node[1]:
            yield from references(child)
    if node[0] == "rep":
        yield from references(node[2])


def describe_generate_rules():
    def it_always_has_a_root():
        assert all("root" in generate_rules(random.Random(seed)) for seed in range(50))

    def it_references_only_defined_rules():
        for seed in range(100):
            rules = generate_rules(random.Random(seed))
            for body in rules.values():
                assert set(references(body)) <= set(rules)

    def it_recurses_only_through_nest():
        for seed in range(100):
            rules = generate_rules(random.Random(seed))
            for name, body in rules.items():
                assert name == "nest" or name not in set(references(body))

    def it_sometimes_has_helpers_and_sometimes_a_nest():
        drawn = [generate_rules(random.Random(seed)) for seed in range(100)]
        assert any(len(rules) > 2 for rules in drawn)
        assert any("nest" in rules for rules in drawn)

    def it_is_deterministic_for_a_seed():
        assert generate_rules(random.Random(9)) == generate_rules(random.Random(9))
