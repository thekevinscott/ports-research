import statistics


def timing_summary(results: list[dict]) -> dict:
    values = sorted(r["elapsed_ns"] for r in results if r["elapsed_ns"] is not None)
    if not values:
        return {"mean_elapsed_ns": None, "p50_elapsed_ns": None, "p95_elapsed_ns": None}
    if len(values) == 1:
        return {"mean_elapsed_ns": values[0], "p50_elapsed_ns": values[0], "p95_elapsed_ns": values[0]}
    percentiles = statistics.quantiles(values, n=100, method="inclusive")
    return {
        "mean_elapsed_ns": statistics.fmean(values),
        "p50_elapsed_ns": percentiles[49],
        "p95_elapsed_ns": percentiles[94],
    }
