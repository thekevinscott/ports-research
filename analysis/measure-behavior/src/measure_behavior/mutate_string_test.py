import random

from measure_behavior.mutate_string import mutate_string


def describe_mutate_string():
    def it_changes_the_string_or_its_length():
        for seed in range(50):
            assert mutate_string("abcd", random.Random(seed)) != "abcd"

    def it_mutates_the_empty_string_into_something():
        assert all(mutate_string("", random.Random(seed)) for seed in range(20))

    def it_is_deterministic_for_a_seed():
        assert mutate_string("abcd", random.Random(3)) == mutate_string("abcd", random.Random(3))
