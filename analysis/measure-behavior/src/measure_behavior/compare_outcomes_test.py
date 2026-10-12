import json

import pytest

from measure_behavior.compare_outcomes import compare_outcomes

OUTCOMES = ("accept", "reject", "error", "crash")


def write(path, outcomes):
    path.write_text("".join(json.dumps({"grammar": g, "input": i, "outcome": o, "error": None}) + "\n" for g, i, o in outcomes))
    return path


def describe_compare_outcomes():
    def it_counts_agreement_over_every_pair(tmp_path):
        reference = write(tmp_path / "r.jsonl", [("g0", 0, "accept"), ("g0", 1, "reject"), ("g1", 0, "error"), ("g1", 1, "accept")])
        port = write(tmp_path / "p.jsonl", [("g1", 1, "accept"), ("g0", 0, "accept"), ("g0", 1, "accept"), ("g1", 0, "crash")])
        report = compare_outcomes(reference=reference, port=port)
        assert (report["pairs"], report["agreements"], report["agreement_rate"]) == (4, 2, 0.5)

    def it_tables_reference_outcome_against_port_outcome(tmp_path):
        reference = write(tmp_path / "r.jsonl", [("g0", 0, "accept"), ("g0", 1, "reject"), ("g1", 0, "error")])
        port = write(tmp_path / "p.jsonl", [("g0", 0, "accept"), ("g0", 1, "accept"), ("g1", 0, "crash")])
        confusion = compare_outcomes(reference=reference, port=port)["confusion"]
        assert list(confusion) == list(OUTCOMES)
        assert all(list(row) == list(OUTCOMES) for row in confusion.values())
        assert confusion["accept"]["accept"] == 1
        assert confusion["reject"]["accept"] == 1
        assert confusion["error"]["crash"] == 1
        assert sum(sum(row.values()) for row in confusion.values()) == 3

    def it_rejects_files_over_different_pairs(tmp_path):
        reference = write(tmp_path / "r.jsonl", [("g0", 0, "accept")])
        port = write(tmp_path / "p.jsonl", [("g0", 1, "accept")])
        with pytest.raises(ValueError, match="different pairs"):
            compare_outcomes(reference=reference, port=port)
