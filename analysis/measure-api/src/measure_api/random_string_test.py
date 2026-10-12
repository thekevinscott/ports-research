import random

from measure_api.random_string import MAX_LENGTH, random_string


def describe_random_string():
    def it_is_the_same_for_the_same_seed():
        assert [random_string(random.Random(4)) for _ in range(5)] == [random_string(random.Random(4)) for _ in range(5)]

    def it_stays_within_the_length_bound():
        rng = random.Random(0)
        assert all(1 <= len(random_string(rng)) <= MAX_LENGTH for _ in range(200))

    def it_varies_across_draws():
        rng = random.Random(0)
        assert len({random_string(rng) for _ in range(20)}) > 1
