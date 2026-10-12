import re


def jaccard_similarity(reference: list[str], port: list[str]) -> list[list[float]]:
    """Each pair's shared lowercased words over all its words: the fallback when no embedding server is reachable."""

    def words(text: str) -> set[str]:
        return set(re.findall(r"\w+", text.lower()))

    def score(a: set[str], b: set[str]) -> float:
        return len(a & b) / len(a | b) if a and b else 0.0

    port_words = [words(p) for p in port]
    return [[score(words(r), p) for p in port_words] for r in reference]
