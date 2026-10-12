from collections.abc import Sequence


def levenshtein(left: Sequence[str], right: Sequence[str]) -> int:
    """Unit-cost insert, delete and substitute over two sequences."""
    row = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        previous, row[0] = row[0], i
        for j, b in enumerate(right, 1):
            previous, row[j] = row[j], min(row[j] + 1, row[j - 1] + 1, previous + (a != b))
    return row[-1]
