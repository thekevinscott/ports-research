import random

SEED = 0


def shuffle_items(items: list[dict]) -> list[dict]:
    """The items in seed-0 shuffled order, the same whatever order they arrive in."""
    shuffled = sorted(items, key=lambda item: item["id"])
    random.Random(SEED).shuffle(shuffled)
    return shuffled
