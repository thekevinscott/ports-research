from pathlib import Path

import pytest

from measure_ast.compare import compare

REFERENCE = b"""\
def f(a):
    if a:
        return 1
    return 2

def g():
    return 1
"""

# g renamed to h; one branch added to f.
PORT = b"""\
def f(a):
    if a:
        return 1
    if a:
        return 3
    return 2

def h():
    return 1
"""


def tree(root: Path, source: bytes) -> Path:
    (root / "pkg").mkdir(parents=True)
    (root / "pkg" / "a.py").write_bytes(source)
    (root / "pkg" / "a_test.py").write_bytes(b"def test_a():\n    pass\n")
    return root


@pytest.fixture
def reference(tmp_path):
    return tree(tmp_path / "reference", REFERENCE)


@pytest.fixture
def port(tmp_path):
    return tree(tmp_path / "port", PORT)


def run(port, reference):
    return compare(language="python", port=port, reference=reference, exclude=["*_test.py"])


def describe_compare():
    def it_reports_the_language_and_both_targets(port, reference):
        report = run(port, reference)
        assert (report["language"], report["port"], report["reference"]) == ("python", str(port), str(reference))

    def it_reports_every_one_tree_measure_as_port_minus_reference_with_both_values(port, reference):
        delta = run(port, reference)["delta"]
        assert set(delta) == {
            "parsed_file_count", "node_count", "max_depth", "function_count",
            "mean_function_lines", "max_function_lines", "mean_cyclomatic", "max_cyclomatic",
        }
        assert all(d["delta"] == d["port"] - d["reference"] for d in delta.values())
        assert (delta["node_count"]["delta"], delta["function_count"]["delta"], delta["max_cyclomatic"]["delta"]) == (5, 0, 1)

    def it_pairs_functions_and_lists_the_unmatched_on_each_side(port, reference):
        functions = run(port, reference)["functions"]
        assert (functions["matched_count"], functions["port_only_count"], functions["reference_only_count"]) == (1, 1, 1)
        assert (functions["port_only"], functions["reference_only"]) == (["h/0"], ["g/0"])
        assert functions["matched_fraction"] == 0.5
        assert functions["median_line_drift"] == 2

    def it_reports_lines_and_tree_edit_distance_per_matched_pair(port, reference):
        assert run(port, reference)["functions"]["matched"] == [
            {
                "port": "f/1",
                "reference": "f/1",
                "port_lines": 6,
                "reference_lines": 4,
                "tree_edit_distance": 5,
                "normalised": 5 / 17,
            }
        ]

    def it_summarises_normalised_tree_edit_distance_over_pairs(port, reference):
        assert run(port, reference)["tree_edit_distance"] == {"mean_normalised": 5 / 17, "median_normalised": 5 / 17}

    def it_reports_both_cyclomatic_distributions_and_their_wasserstein_distance(port, reference):
        assert run(port, reference)["branching"] == {"port": [1, 3], "reference": [1, 2], "wasserstein": 0.5}

    def it_diffs_the_api_surface(port, reference):
        assert run(port, reference)["api_surface"] == {"shared": ["f/1"], "port_only": ["h/0"], "reference_only": ["g/0"]}

    def it_traces_call_paths_from_the_shared_api_surface(port, reference):
        call_paths = run(port, reference)["call_paths"]
        assert call_paths["entry_point_count"] == 1
        assert call_paths["entry_points"][0]["entry_point"] == "f"
        assert call_paths["explainer"] == ["f: reference trace of 1 (f); port 1, missing none, extra none"]
        assert call_paths["unreachable_port_only"] == ["h/0"]

    def it_is_all_zero_against_itself(reference):
        report = run(reference, reference)
        assert all(d["delta"] == 0 for d in report["delta"].values())
        assert report["functions"]["matched_fraction"] == 1
        assert [pair["tree_edit_distance"] for pair in report["functions"]["matched"]] == [0, 0]
        assert report["branching"]["wasserstein"] == 0

    def it_reports_nones_when_a_side_has_no_functions(tmp_path, reference):
        empty = tmp_path / "empty"
        empty.mkdir()
        (empty / "a.py").write_bytes(b"x = 1\n")
        report = run(reference, empty)
        assert report["functions"]["matched_fraction"] is None
        assert report["functions"]["median_line_drift"] is None
        assert report["tree_edit_distance"] == {"mean_normalised": None, "median_normalised": None}
        assert report["branching"]["wasserstein"] is None

    def it_raises_when_a_side_has_no_source(tmp_path, reference):
        (tmp_path / "nothing").mkdir()
        with pytest.raises(FileNotFoundError, match="no python source"):
            run(tmp_path / "nothing", reference)
