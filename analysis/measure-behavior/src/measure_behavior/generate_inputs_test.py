import random

from measure_behavior.generate_inputs import generate_inputs

RULES = {"root": ("seq", (("lit", "ab"), ("rep", "?", ("lit", "c"))))}


def describe_generate_inputs():
    def it_includes_strings_drawn_from_the_grammar():
        inputs = generate_inputs(RULES, random.Random(0), 10)
        assert {"ab", "abc"} & set(inputs)

    def it_includes_strings_drawn_from_outside_the_grammar():
        inputs = generate_inputs(RULES, random.Random(0), 10)
        assert set(inputs) - {"ab", "abc"}

    def it_includes_the_empty_string():
        assert "" in generate_inputs(RULES, random.Random(0), 10)

    def it_has_no_duplicates_and_at_most_count():
        inputs = generate_inputs(RULES, random.Random(0), 6)
        assert len(inputs) == len(set(inputs)) <= 6
