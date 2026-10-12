from collections.abc import Callable
from functools import cache
from math import sqrt


def embedding_similarity(embed: Callable[[str], list[float]]) -> Callable[[list[str], list[str]], list[list[float]]]:
    """Cosine similarity of each pair's embeddings; each distinct text is embedded once for the life of the function."""

    @cache
    def unit(text: str) -> tuple[float, ...]:
        vector = embed(text)
        norm = sqrt(sum(x * x for x in vector)) or 1.0
        return tuple(x / norm for x in vector)

    def similarity(reference: list[str], port: list[str]) -> list[list[float]]:
        return [[sum(a * b for a, b in zip(unit(r), unit(p))) for p in port] for r in reference]

    return similarity
