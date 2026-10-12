import random

from measure_behavior.corrupt_grammar import corrupt_grammar

GRAMMAR = 'root ::= "a" item\nitem ::= [a-z]\n'


def describe_corrupt_grammar():
    def it_always_changes_the_grammar():
        for seed in range(50):
            assert corrupt_grammar(GRAMMAR, random.Random(seed)) != GRAMMAR

    def it_reaches_every_kind_of_corruption():
        assert len({corrupt_grammar(GRAMMAR, random.Random(seed)) for seed in range(200)}) >= 10

    def it_is_deterministic_for_a_seed():
        assert corrupt_grammar(GRAMMAR, random.Random(7)) == corrupt_grammar(GRAMMAR, random.Random(7))
