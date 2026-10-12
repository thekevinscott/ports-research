from walkthroughs.compare_walkthroughs import compare_walkthroughs

OFFSETS = (-0.1, -0.05, 0.0, 0.05, 0.1)


def sweep_thresholds(reference: dict, port: dict, similarity: dict) -> list[dict]:
    """The per-section means of compare_walkthroughs with the match threshold moved by each offset."""
    swept = []
    for offset in OFFSETS:
        threshold = round(similarity["threshold"] + offset, 4)
        compared = compare_walkthroughs(reference, port, {**similarity, "threshold": threshold})
        swept.append({"threshold": threshold, **{k: compared[k] for k in ("mean_coverage", "mean_order_agreement", "error_paths", "invariants")}})
    return swept
