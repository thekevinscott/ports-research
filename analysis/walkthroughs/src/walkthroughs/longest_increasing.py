from bisect import bisect_left


def longest_increasing(values: list[int]) -> int:
    """The length of the longest strictly increasing subsequence."""
    tails: list[int] = []
    for value in values:
        i = bisect_left(tails, value)
        tails[i:i + 1] = [value]
    return len(tails)
