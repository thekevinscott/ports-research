import statistics

PHASES = ("construct_ns", "add_ns")


def _phase_summary(values: list[int]) -> dict:
    median = statistics.median(values)
    if len(values) == 1:
        return {"median": values[0], "p90": values[0], "min": values[0], "spread": 0.0}
    percentiles = statistics.quantiles(values, n=100, method="inclusive")
    p10, p90 = percentiles[9], percentiles[89]
    return {
        "median": median,
        "p90": p90,
        "min": min(values),
        "spread": None if median == 0 else (p90 - p10) / median,
    }


def ladder_summary(*, cases: list[dict], results: list[dict]) -> list[dict]:
    return [
        {
            "rung": case.get("rung"),
            "input_len": len(case["input"]),
            **{phase: _phase_summary(result[phase]) for phase in PHASES},
        }
        for case, result in zip(cases, results)
        if all(result.get(phase) and None not in result[phase] for phase in PHASES)
    ]
