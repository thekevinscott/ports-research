import pytest

from walkthroughs.compare_walkthroughs import compare_walkthroughs


def same_text(reference, port):
    """A fake similarity: 1 for identical steps, 0 otherwise."""
    return [[1.0 if r == p else 0.0 for p in port] for r in reference]


SIMILARITY = {"name": "fake", "threshold": 0.8, "score": same_text}


def entry(name, happy=(), errors=(), invariants=()):
    return {"name": name, "happy_path": list(happy), "error_paths": list(errors), "invariants": list(invariants)}


def describe_compare_walkthroughs():
    def it_pairs_entry_points_by_name_without_underscores_or_case():
        reference = {"entry_points": [entry("parse_grammar", ["a", "b"]), entry("GBNF.print", ["c"]), entry("helper")]}
        port = {"entry_points": [entry("parseGrammar", ["a"]), entry("gbnf.print", ["c"]), entry("extra")]}
        compared = compare_walkthroughs(reference, port, SIMILARITY)
        assert [(e["reference"], e["port"]) for e in compared["entry_points"]] == [("parse_grammar", "parseGrammar"), ("GBNF.print", "gbnf.print")]
        assert compared["entry_points_matched"] == 2
        assert compared["entry_points_reference_only"] == ["helper"]
        assert compared["entry_points_port_only"] == ["extra"]

    def it_aligns_each_section_of_a_pair_on_its_own():
        reference = {"entry_points": [entry("f", happy=["a", "b"], errors=["e"], invariants=["i", "j"])]}
        port = {"entry_points": [entry("f", happy=["b", "a", "x"], errors=[], invariants=["j"])]}
        [pair] = compare_walkthroughs(reference, port, SIMILARITY)["entry_points"]
        assert pair["happy_path"]["coverage"] == 1.0
        assert pair["happy_path"]["order_agreement"] == 0.5
        assert pair["happy_path"]["extra_steps"] == ["x"]
        assert (pair["error_paths"]["coverage"], pair["error_paths"]["missing_steps"]) == (0.0, ["e"])
        assert (pair["invariants"]["coverage"], pair["invariants"]["missing_steps"]) == (0.5, ["i"])

    def it_averages_coverage_and_order_over_the_matched_pairs_per_section():
        reference = {"entry_points": [entry("f", happy=["a", "b"]), entry("g", happy=["c", "d"], errors=["e"]), entry("h")]}
        port = {"entry_points": [entry("f", happy=["b", "a"]), entry("g", happy=["c"]), entry("h")]}
        compared = compare_walkthroughs(reference, port, SIMILARITY)
        assert compared["mean_coverage"] == pytest.approx(0.75)
        assert compared["mean_order_agreement"] == pytest.approx(0.75)
        assert compared["error_paths"] == {"mean_coverage": 0.0, "mean_order_agreement": None}
        assert compared["invariants"] == {"mean_coverage": None, "mean_order_agreement": None}

    def it_records_the_similarity_and_threshold_it_used():
        compared = compare_walkthroughs({"entry_points": []}, {"entry_points": []}, SIMILARITY)
        assert (compared["similarity"], compared["threshold"], compared["mean_coverage"]) == ("fake", 0.8, None)
