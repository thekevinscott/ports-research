from statistics import fmean, median

from measure_ast.call_graph import CallGraph
from measure_ast.label import label
from measure_ast.levenshtein import levenshtein


def edges(graph: CallGraph, trace: list[int]) -> dict[tuple[str, str], str]:
    """Every call edge out of the traced functions, normalised endpoints to `caller->callee`, in trace order."""
    found = {}
    for i in trace:
        for j in graph.edges[i]:
            caller, callee = graph.functions[i], graph.functions[j]
            found.setdefault((caller.key, callee.key), f"{caller.name}->{callee.name}")
    return found


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def entry_point(name: str, reference: CallGraph, port: CallGraph, starts: dict[str, int | None]) -> dict:
    traces = {
        side: graph.trace(starts[side]) if starts[side] is not None else []
        for side, graph in (("reference", reference), ("port", port))
    }
    reference_edges, port_edges = edges(reference, traces["reference"]), edges(port, traces["port"])
    shared = reference_edges.keys() & port_edges.keys()
    distance = levenshtein(
        [reference.functions[i].key for i in traces["reference"]], [port.functions[i].key for i in traces["port"]]
    )
    return {
        "entry_point": name,
        "reference_trace": [reference.functions[i].name for i in traces["reference"]],
        "port_trace": [port.functions[i].name for i in traces["port"]],
        "trace_edit_distance": distance,
        "trace_normalised": distance / max(len(traces["reference"]), len(traces["port"])),
        "reference_edges": len(reference_edges),
        "port_edges": len(port_edges),
        "edge_recall": ratio(len(shared), len(reference_edges)),
        "edge_precision": ratio(len(shared), len(port_edges)),
        "missing_edges": [edge for key, edge in reference_edges.items() if key not in shared],
        "extra_edges": [edge for key, edge in port_edges.items() if key not in shared],
        "reachable_reference": len(traces["reference"]),
        "reachable_port": len(traces["port"]),
    }


def explain(entry: dict) -> str:
    return (
        f"{entry['entry_point']}: reference trace of {entry['reachable_reference']} ({', '.join(entry['reference_trace'])}); "
        f"port {entry['reachable_port']}, missing {', '.join(entry['missing_edges']) or 'none'}, "
        f"extra {', '.join(entry['extra_edges']) or 'none'}"
    )


def call_paths(*, reference: CallGraph, port: CallGraph, shared: list[str]) -> dict:
    """Trace each shared function or class from its entry point on both sides and compare the call paths."""
    starts: dict[str, dict[str, int | None]] = {}
    for entry in shared:
        for side, graph in (("reference", reference), ("port", port)):
            for i in graph.entry_points(entry):
                fn = graph.functions[i]
                start = starts.setdefault(fn.key, {"name": fn.name, "reference": None, "port": None})
                start[side] = i
    entries = [entry_point(start["name"], reference, port, start) for start in starts.values()]
    reached = {
        side: {i for start in starts.values() if start[side] is not None for i in graph.trace(start[side])}
        for side, graph in (("reference", reference), ("port", port))
    }
    recalls = [e["edge_recall"] for e in entries if e["edge_recall"] is not None]
    return {
        "entry_point_count": len(entries),
        "mean_edge_recall": fmean(recalls) if recalls else None,
        "median_trace_normalised": median(e["trace_normalised"] for e in entries) if entries else None,
        "reachable_fraction_reference": ratio(len(reached["reference"]), len(reference.functions)),
        "reachable_fraction_port": ratio(len(reached["port"]), len(port.functions)),
        "unreachable_port_only": sorted(
            label(fn.name, fn.arity) for i, fn in enumerate(port.functions) if i not in reached["port"]
        ),
        "entry_points": entries,
        "explainer": [explain(e) for e in entries],
    }
