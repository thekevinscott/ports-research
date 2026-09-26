from collections.abc import Callable
from pathlib import Path

from .compare_targets import compare_targets
from .run_driver import run_driver


def exercise_api(
    *,
    language: str,
    reference: Path,
    targets: list[Path],
    cases: list[dict],
    adapt: bool,
    timeout: float,
    memory_limit_bytes: int,
    repeat: int = 1,
    warmup: int = 0,
    checkpoint: Callable[[dict], None] = lambda report: None,
) -> dict:
    run = dict(
        language=language,
        cases=cases,
        timeout=timeout,
        memory_limit_bytes=memory_limit_bytes,
        repeat=repeat,
        warmup=warmup,
    )
    reference_results = run_driver(target=reference, adapt=False, **run)
    target_results = {}
    report = {}
    for target in targets:
        target_results[str(target)] = run_driver(target=target, adapt=adapt, **run)
        report = {
            "language": language,
            "reference": str(reference),
            **compare_targets(cases=cases, reference=reference_results, targets=target_results),
        }
        checkpoint(report)
    return report
