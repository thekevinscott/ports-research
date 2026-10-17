import json
import shutil
import subprocess
from itertools import chain
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
# The notebook's python exclude list (analysis/notebook/src/corpus.py EXCLUDE).
EXCLUDE = [
    "node_modules", "__pycache__", ".venv", ".pytest_cache", "dist", "dev-deps", "tests", "test",
    "integration-tests", "conftest.py", "*_test.py", "test_*.py", "*.test.ts", "*.spec.ts",
]
BRANCH = "    if value is None:\n        return value\n"


def run_compare(port: Path, reference: Path) -> dict:
    result = subprocess.run(
        [
            "uv", "run", "measure-ast", "compare", "--language", "python",
            "--port", str(port), "--reference", str(reference),
            *chain.from_iterable(("--exclude", pattern) for pattern in EXCLUDE),
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


@pytest.fixture(scope="module")
def against_itself(python_reference):
    return run_compare(python_reference, python_reference)


@pytest.fixture(scope="module")
def edited_port(python_reference, tmp_path_factory):
    port = tmp_path_factory.mktemp("port").resolve() / "python"
    shutil.copytree(python_reference, port)
    renamed = port / "gbnf" / "rules_builder" / "is_word_char.py"
    renamed.write_text(renamed.read_text().replace("def is_word_char(", "def is_letter("))
    branched = port / "gbnf" / "utils" / "validate_non_empty.py"
    head, body = branched.read_text().split("\n", 1)
    branched.write_text(f"{head}\n{BRANCH}{body}")
    return port


@pytest.fixture(scope="module")
def against_edit(edited_port, python_reference):
    return run_compare(edited_port, python_reference)


def describe_compare_of_the_python_reference_against_itself():
    def it_reports_every_delta_as_zero(against_itself):
        assert {name: d["delta"] for name, d in against_itself["delta"].items()} == dict.fromkeys(
            against_itself["delta"], 0
        )
        assert against_itself["delta"]["function_count"]["reference"] > 0

    def it_matches_every_function(against_itself):
        functions = against_itself["functions"]
        assert (functions["port_only_count"], functions["reference_only_count"]) == (0, 0)
        assert functions["matched_fraction"] == 1
        assert functions["matched_count"] == len(functions["matched"]) > 0

    def it_reports_every_distance_as_zero(against_itself):
        assert {pair["tree_edit_distance"] for pair in against_itself["functions"]["matched"]} == {0}
        assert against_itself["tree_edit_distance"] == {"mean_normalised": 0, "median_normalised": 0}
        assert against_itself["branching"]["wasserstein"] == 0

    def it_shares_the_whole_api_surface(against_itself):
        api = against_itself["api_surface"]
        assert (api["port_only"], api["reference_only"]) == ([], [])
        assert "is_word_char/1" in api["shared"]

    def it_traces_every_entry_point_identically(against_itself):
        call_paths = against_itself["call_paths"]
        assert call_paths["entry_point_count"] == len(call_paths["entry_points"]) > 0
        assert call_paths["mean_edge_recall"] == 1
        assert call_paths["median_trace_normalised"] == 0
        assert {(e["trace_edit_distance"], len(e["missing_edges"]), len(e["extra_edges"])) for e in call_paths["entry_points"]} == {(0, 0, 0)}
        assert call_paths["reachable_fraction_reference"] == call_paths["reachable_fraction_port"] > 0


def describe_compare_of_the_python_reference_against_a_renamed_and_branched_copy():
    def it_unmatches_the_renamed_function_on_both_sides(against_edit, against_itself):
        functions = against_edit["functions"]
        assert (functions["port_only"], functions["reference_only"]) == (["is_letter/1"], ["is_word_char/1"])
        assert functions["matched_count"] == against_itself["functions"]["matched_count"] - 1

    def it_charges_the_added_branch_to_its_function_alone(against_edit):
        distances = {pair["reference"]: pair["tree_edit_distance"] for pair in against_edit["functions"]["matched"]}
        assert distances.pop("validate_non_empty/1") == 7
        assert set(distances.values()) == {0}

    def it_adds_the_branch_nodes_and_one_cyclomatic_point(against_edit):
        delta = against_edit["delta"]
        function_count = delta["function_count"]["reference"]
        assert (delta["function_count"]["delta"], delta["node_count"]["delta"]) == (0, 7)
        assert delta["mean_cyclomatic"]["delta"] == pytest.approx(1 / function_count)
        assert against_edit["branching"]["wasserstein"] == pytest.approx(1 / function_count)

    def it_diffs_the_renamed_function_in_the_api_surface(against_edit):
        api = against_edit["api_surface"]
        assert (api["port_only"], api["reference_only"]) == (["is_letter/1"], ["is_word_char/1"])

    def it_misses_the_call_edges_into_the_renamed_function(against_edit):
        call_paths = against_edit["call_paths"]
        missing = {edge for entry in call_paths["entry_points"] for edge in entry["missing_edges"]}
        assert {edge.split("->")[1] for edge in missing} == {"is_word_char"}
        assert "parse_name->is_word_char" in missing
        assert all(entry["extra_edges"] == [] for entry in call_paths["entry_points"])
        assert "is_letter/1" in call_paths["unreachable_port_only"]
