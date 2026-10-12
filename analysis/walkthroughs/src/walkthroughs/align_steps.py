from collections.abc import Callable

from walkthroughs.longest_increasing import longest_increasing


def align_steps(reference: list[str], port: list[str], *, similarity: Callable[[list[str], list[str]], list[list[float]]], threshold: float) -> dict:
    """Match port steps to reference steps one-to-one, most similar pair first, and score coverage and order.

    Ties go to the pair nearest in relative position, so order is kept where the scores allow it.
    order_agreement is the longest increasing run of matched port positions, taken in reference order, over the matches.
    """
    scores = similarity(reference, port) if reference and port else []
    candidates = sorted(
        (
            (-score, abs(i / len(reference) - j / len(port)), i, j)
            for i, row in enumerate(scores)
            for j, score in enumerate(row)
            if score >= threshold
        )
    )
    matched_reference, matched_port, matches = set(), set(), []
    for negative, _, i, j in candidates:
        if i not in matched_reference and j not in matched_port:
            matched_reference.add(i)
            matched_port.add(j)
            matches.append({"reference": i, "port": j, "similarity": -negative})
    matches.sort(key=lambda m: m["reference"])
    return {
        "coverage": len(matches) / len(reference) if reference else None,
        "order_agreement": longest_increasing([m["port"] for m in matches]) / len(matches) if matches else None,
        "extra_steps": [step for j, step in enumerate(port) if j not in matched_port],
        "missing_steps": [step for i, step in enumerate(reference) if i not in matched_reference],
        "matches": matches,
    }
