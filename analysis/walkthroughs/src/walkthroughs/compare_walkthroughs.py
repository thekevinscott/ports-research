from statistics import mean

from walkthroughs.align_steps import align_steps

SECTIONS = ("happy_path", "error_paths", "invariants")


def compare_walkthroughs(reference: dict, port: dict, similarity: dict) -> dict:
    """Pair entry points by name with underscores and case dropped, align each section's steps, and average over the pairs."""

    def key(entry: dict) -> str:
        return entry["name"].replace("_", "").lower()

    unpaired = list(port["entry_points"])
    pairs, reference_only = [], []
    for entry in reference["entry_points"]:
        match = next((p for p in unpaired if key(p) == key(entry)), None)
        if match is None:
            reference_only.append(entry["name"])
            continue
        unpaired.remove(match)
        aligned = {s: align_steps(entry[s], match[s], similarity=similarity["score"], threshold=similarity["threshold"]) for s in SECTIONS}
        pairs.append({"reference": entry["name"], "port": match["name"], **aligned})

    def averages(section: str) -> dict:
        def average(measure: str) -> float | None:
            values = [p[section][measure] for p in pairs if p[section][measure] is not None]
            return mean(values) if values else None

        return {"mean_coverage": average("coverage"), "mean_order_agreement": average("order_agreement")}

    return {
        "similarity": similarity["name"],
        "threshold": similarity["threshold"],
        "embeddings": similarity["embeddings"],
        **averages("happy_path"),
        "error_paths": averages("error_paths"),
        "invariants": averages("invariants"),
        "entry_points_matched": len(pairs),
        "entry_points_reference_only": reference_only,
        "entry_points_port_only": [p["name"] for p in unpaired],
        "entry_points": pairs,
    }
