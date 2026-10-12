import json

import pytest

from measure_api.compare_cases import compare_cases

OUTCOMES = ("match", "mismatch", "error_match", "error_mismatch", "crash")
STATUSES = ("ok", "error", "crash")
OK = [{"step": "construct", "rules": [{"type": "char", "value": [97]}]}]
OTHER = [{"step": "construct", "rules": [{"type": "char", "value": [98]}]}]
RAISED = [{"step": "construct", "error": {"class": "GrammarParseError", "pos": 0}}]


def write(path, cases):
    lines = [{"grammar": g, "input": i, "steps": None if s is None else s, "crash": "exit 1" if s is None else None} for g, i, s in cases]
    path.write_text("".join(json.dumps(line) + "\n" for line in lines))
    return path


def describe_compare_cases():
    def it_counts_match_and_error_match_as_agreement(tmp_path):
        reference = write(tmp_path / "r.jsonl", [("g0", 0, OK), ("g0", 1, RAISED), ("g1", 0, OK), ("g1", 1, OK)])
        port = write(tmp_path / "p.jsonl", [("g1", 1, None), ("g0", 0, OK), ("g0", 1, RAISED), ("g1", 0, OTHER)])
        report = compare_cases(reference=reference, port=port)
        assert (report["cases"], report["agreements"], report["agreement_rate"]) == (4, 2, 0.5)
        assert report["outcomes"] == {"match": 1, "mismatch": 1, "error_match": 1, "error_mismatch": 0, "crash": 1}

    def it_tables_reference_status_against_port_status(tmp_path):
        reference = write(tmp_path / "r.jsonl", [("g0", 0, OK), ("g0", 1, RAISED), ("g0", 2, OK)])
        port = write(tmp_path / "p.jsonl", [("g0", 0, RAISED), ("g0", 1, RAISED), ("g0", 2, None)])
        confusion = compare_cases(reference=reference, port=port)["confusion"]
        assert list(confusion) == list(STATUSES)
        assert all(list(row) == list(STATUSES) for row in confusion.values())
        assert (confusion["ok"]["error"], confusion["error"]["error"], confusion["ok"]["crash"]) == (1, 1, 1)
        assert sum(sum(row.values()) for row in confusion.values()) == 3

    def it_records_the_first_differing_step_and_both_sides(tmp_path):
        reference = write(tmp_path / "r.jsonl", [("g0", 0, OK)])
        port = write(tmp_path / "p.jsonl", [("g0", 0, OTHER)])
        assert compare_cases(reference=reference, port=port)["disagreements"] == [
            {"grammar": "g0", "input": 0, "outcome": "mismatch", "step": 0, "reference": OK[0], "port": OTHER[0]}
        ]

    def it_rejects_files_over_different_cases(tmp_path):
        reference = write(tmp_path / "r.jsonl", [("g0", 0, OK)])
        port = write(tmp_path / "p.jsonl", [("g0", 1, OK)])
        with pytest.raises(ValueError, match="different cases"):
            compare_cases(reference=reference, port=port)

    def it_lists_every_outcome_even_when_none_occur(tmp_path):
        reference = write(tmp_path / "r.jsonl", [("g0", 0, OK)])
        assert list(compare_cases(reference=reference, port=reference)["outcomes"]) == list(OUTCOMES)
