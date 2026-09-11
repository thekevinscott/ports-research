from .generate_grammar import generate_grammar


def build_corpus(*, sizes: list[int], nesting_depth: int, alternation_width: int, seed: int) -> list[dict]:
    """A grammar of each requested size, in the same order as `sizes`."""
    return [
        {
            "size": size,
            "grammar": generate_grammar(
                rule_count=size,
                nesting_depth=nesting_depth,
                alternation_width=alternation_width,
                seed=seed,
            ),
        }
        for size in sizes
    ]
