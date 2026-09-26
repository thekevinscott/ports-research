from pathlib import Path

from .build_corpus import build_corpus
from .corpus_sizes import corpus_sizes
from .log_log_slope import log_log_slope
from .measure_python_curve import measure_python_curve
from .measure_typescript_curve import measure_typescript_curve


def run_complexity_curve(
    *,
    language: str,
    target: Path,
    max_size: int,
    steps: int,
    nesting_depth: int,
    alternation_width: int,
    iterations: int,
    seed: int,
) -> dict:
    """Fingerprint target's time-complexity shape: measure parse time across a
    corpus of grammars of increasing size, then fit a log-log slope — the
    shape is comparable across languages even though the absolute times
    are not.

    The driver lookup is built here, not at module scope: a module-scope dict
    would capture measure_python_curve/measure_typescript_curve once at
    import time, so patching either name later (as every unit test here does)
    would silently miss it.
    """
    drivers = {
        "python": measure_python_curve,
        "typescript": measure_typescript_curve,
    }
    sizes = corpus_sizes(max_size=max_size, steps=steps)
    corpus = build_corpus(
        sizes=sizes, nesting_depth=nesting_depth, alternation_width=alternation_width, seed=seed
    )
    curve = drivers[language](target=target, corpus=corpus, iterations=iterations)
    slope = log_log_slope(
        sizes=[point["size"] for point in curve],
        seconds=[point["seconds"] for point in curve],
    )
    return {
        "language": language,
        "target": str(target),
        "curve": curve,
        "log_log_slope": slope,
    }
