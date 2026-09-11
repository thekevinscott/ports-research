from .ladder_summary import ladder_summary
from .outcome_key import outcome_key
from .timing_summary import timing_summary

DISAGREEMENT_LIMIT = 20
TIMING_KEYS = {"elapsed_ns", "construct_ns", "add_ns"}


def _without_timing(result: dict) -> dict:
    return {k: v for k, v in result.items() if k not in TIMING_KEYS}


def _repeated(results: list[dict]) -> bool:
    return any(isinstance(result.get("add_ns"), list) for result in results)


def compare_targets(*, cases: list[dict], reference: list[dict], targets: dict[str, list[dict]]) -> dict:
    reference_keys = [outcome_key(r) for r in reference]
    reference_timing = {f"reference_{k}": v for k, v in timing_summary(reference).items()}
    if _repeated(reference):
        reference_timing["reference_timings"] = ladder_summary(cases=cases, results=reference)
    reference_errors = sum(not r["ok"] for r in reference)
    target_keys = {name: [outcome_key(r) for r in results] for name, results in targets.items()}

    report = {"cases": len(cases), "targets": {}}
    for name, results in targets.items():
        disagreeing = [i for i, key in enumerate(target_keys[name]) if key != reference_keys[i]]
        report["targets"][name] = {
            "cases": len(cases),
            "agree_with_reference": len(cases) - len(disagreeing),
            "disagree_with_reference": len(disagreeing),
            "disagreements": [
                {"case": cases[i], "reference": _without_timing(reference[i]), "target": _without_timing(results[i])}
                for i in disagreeing[:DISAGREEMENT_LIMIT]
            ],
            "reference_error_cases": reference_errors,
            "target_error_cases": sum(not r["ok"] for r in results),
            **reference_timing,
            **{f"target_{k}": v for k, v in timing_summary(results).items()},
            **({"timings": ladder_summary(cases=cases, results=results)} if _repeated(results) else {}),
        }

    if len(targets) > 1:
        unanimous = [i for i in range(len(cases)) if len({keys[i] for keys in target_keys.values()}) == 1]
        report["agree_all_targets"] = len(unanimous)
        report["agree_all_targets_not_reference"] = sum(
            next(iter(target_keys.values()))[i] != reference_keys[i] for i in unanimous
        )
    return report
