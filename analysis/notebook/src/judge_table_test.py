import json

from src.judge_table import (
    baseline_rows,
    fidelity_runs,
    load,
    per_run,
    split,
    unsure,
    verdict_counts,
)

CONDITIONS = [("neither", False, False), ("unit tests", True, False), ("target integration tests", False, True), ("both", True, True)]
FLAGS = ["include_unit_tests", "include_target_integration_tests"]
SOURCES = ["python", "javascript"]


def entry(run, source="python", unit=False, target=False, baseline=False):
    return {
        "run": run,
        "baseline": baseline,
        "source_language": source,
        "target_language": "javascript" if source == "python" else "python",
        "include_unit_tests": None if baseline else unit,
        "include_source_integration_tests": None if baseline else False,
        "include_target_integration_tests": None if baseline else target,
    }


def write(tmp_path, judged):
    (tmp_path / "manifest.json").write_text(json.dumps({item_id: e for item_id, e, _ in judged}))
    (tmp_path / "judgments.jsonl").write_text(
        "\n".join(json.dumps({"id": item_id, "rubric": "code", "verdicts": v}) for item_id, _, v in judged) + "\n"
    )
    return load(tmp_path)


def describe_load():
    def it_joins_each_judgment_to_its_manifest_entry(tmp_path):
        items = write(tmp_path, [("item-1", entry("r1"), {"q": {"verdict": "a"}})])
        assert items == [{"id": "item-1", **entry("r1"), "verdicts": {"q": {"verdict": "a"}}}]


def describe_split():
    def it_separates_runs_baselines_and_unmatched(tmp_path):
        items = write(
            tmp_path,
            [
                ("item-1", entry("r1"), {}),
                ("item-2", entry(None, baseline=True), {}),
                ("item-3", entry("pilot"), {}),
            ],
        )
        runs, baselines, unmatched = split(items, {"r1"})
        assert [i["id"] for i in runs] == ["item-1"]
        assert [i["id"] for i in baselines] == ["item-2"]
        assert [i["id"] for i in unmatched] == ["item-3"]


def describe_verdict_counts():
    def it_counts_each_value_per_cell_with_every_cell_present(tmp_path):
        items = write(
            tmp_path,
            [
                ("item-1", entry("r1", unit=True), {"q": {"verdict": "a"}}),
                ("item-2", entry("r2", unit=True), {"q": {"verdict": "b"}}),
                ("item-3", entry("r3", source="javascript", target=True), {"q": {"verdict": "a"}}),
            ],
        )
        frame = verdict_counts(items, "q", ["a", "b", "c"], CONDITIONS, FLAGS, SOURCES)
        assert frame.columns == ["source_language", "condition", "n", "a", "b", "c"]
        assert frame.height == 8
        rows = {(r["source_language"], r["condition"]): r for r in frame.iter_rows(named=True)}
        assert rows[("python", "unit tests")] == {"source_language": "python", "condition": "unit tests", "n": 2, "a": 1, "b": 1, "c": 0}
        assert rows[("javascript", "target integration tests")]["a"] == 1
        assert rows[("python", "neither")]["n"] == 0

    def it_counts_every_value_of_a_list_verdict(tmp_path):
        items = write(tmp_path, [("item-1", entry("r1"), {"q": {"verdict": ["b", "a"]}})])
        row = verdict_counts(items, "q", ["a", "b"], CONDITIONS, FLAGS, SOURCES).row(0, named=True)
        assert (row["n"], row["a"], row["b"]) == (1, 1, 1)

    def it_names_integer_values_as_strings(tmp_path):
        items = write(tmp_path, [("item-1", entry("r1"), {"fidelity": {"verdict": 4}})])
        row = verdict_counts(items, "fidelity", [1, 2, 3, 4, 5], CONDITIONS, FLAGS, SOURCES).row(0, named=True)
        assert (row["4"], row["3"]) == (1, 0)


def describe_fidelity_runs():
    def it_gives_one_row_per_run_with_its_condition(tmp_path):
        items = write(tmp_path, [("item-1", entry("r1", target=True), {"fidelity": {"verdict": 3}})])
        assert fidelity_runs(items, CONDITIONS, FLAGS).to_dicts() == [
            {"run_id": "r1", "source_language": "python", "target_language": "javascript", "condition": "target integration tests", "fidelity": 3}
        ]


def describe_per_run():
    def it_joins_list_verdicts_with_plus(tmp_path):
        items = write(tmp_path, [("item-1", entry("r1"), {"q": {"verdict": ["a", "b"]}, "p": {"verdict": "x"}})])
        assert per_run(items, ["q", "p"], CONDITIONS, FLAGS).to_dicts() == [
            {"run_id": "r1", "item": "item-1", "source_language": "python", "condition": "neither", "q": "a+b", "p": "x"}
        ]


def describe_baseline_rows():
    def it_labels_each_baseline_by_direction(tmp_path):
        items = write(tmp_path, [("item-2", entry(None, baseline=True), {"q": {"verdict": "a"}, "fidelity": {"verdict": 4}})])
        assert baseline_rows(items, ["q", "fidelity"]).to_dicts() == [
            {"baseline": "human python (A) vs human javascript (B)", "item": "item-2", "q": "a", "fidelity": "4"}
        ]


def describe_unsure():
    def it_lists_each_unsure_question_with_its_run(tmp_path):
        items = write(
            tmp_path,
            [("item-1", entry("r1"), {"q": {"verdict": ["a"], "confidence": "unsure"}, "p": {"verdict": "x", "confidence": "sure"}})],
        )
        assert unsure(items, ["q", "p"]).to_dicts() == [
            {"run_id": "r1", "item": "item-1", "source_language": "python", "question": "q", "verdict": "a"}
        ]
