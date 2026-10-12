import random

from measure_behavior.generate_atom import generate_atom


def describe_generate_atom():
    def it_draws_literals_classes_and_references():
        kinds = {generate_atom(random.Random(seed), ["item"])[0] for seed in range(100)}
        assert kinds == {"lit", "cls", "ref"}

    def it_draws_no_reference_when_none_is_available():
        assert all(generate_atom(random.Random(seed), [])[0] != "ref" for seed in range(100))

    def it_never_draws_an_empty_literal():
        for seed in range(100):
            atom = generate_atom(random.Random(seed), [])
            assert atom[0] != "lit" or atom[1]
