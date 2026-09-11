from pathlib import Path
from unittest.mock import patch

import polars as pl
import pytest

from src.port_pairs import (
    label_conditions,
    pairs_by_port,
    within_cell,
    within_direction_pairs,
    within_direction_similarity,
)

DIFF_REPORT = {"similarity_pct": 76.19, "identical": 2, "modified": 7}


class StubPort:
    """Stands in for a Codebase built from a run, so the pairing runs without a tree."""

    def __init__(self, run_id, source_language="python", python_tests=False, typescript_tests=False):
        self.language = "typescript" if source_language == "python" else "python"
        self.path = Path(f"/runs/{run_id}/ported_implementation")
        self.exclude = ["node_modules", "*_test.py"]
        self.run = {
            "run_id": run_id,
            "source_language": source_language,
            "target_language": self.language,
            "include_python_tests": python_tests,
            "include_typescript_tests": typescript_tests,
        }


def run_ids(pairs):
    return [(a.run["run_id"], b.run["run_id"]) for a, b in pairs]


@pytest.fixture
def cell():
    return [StubPort(f"run-{index}") for index in range(5)]


@pytest.fixture
def git_diff():
    with patch("src.port_pairs.run_git_diff", autospec=True) as m:
        m.return_value = DIFF_REPORT
        yield m


def describe_within_direction_pairs():
    def it_pairs_every_run_in_a_direction_once(cell):
        assert len(within_direction_pairs(cell)) == 10

    def it_pairs_a_run_with_itself_never(cell):
        assert all(a is not b for a, b in within_direction_pairs(cell))

    def it_counts_a_pair_once_whichever_way_round(cell):
        pairs = run_ids(within_direction_pairs(cell))
        assert not {tuple(reversed(pair)) for pair in pairs} & set(pairs)

    def it_orders_each_pair_by_run_id(cell):
        ports = [cell[3], cell[0], cell[4], cell[1], cell[2]]
        assert all(a < b for a, b in run_ids(within_direction_pairs(ports)))

    def it_pairs_only_within_one_target_language():
        ports = [StubPort("a"), StubPort("b"), StubPort("c", source_language="typescript")]
        assert run_ids(within_direction_pairs(ports)) == [("a", "b")]

    def it_pairs_across_conditions():
        ports = [StubPort("a"), StubPort("b", python_tests=True)]
        assert run_ids(within_direction_pairs(ports)) == [("a", "b")]

    def it_pairs_inside_every_direction():
        ports = [
            StubPort("a"),
            StubPort("b"),
            StubPort("c", source_language="typescript"),
            StubPort("d", source_language="typescript"),
        ]
        assert run_ids(within_direction_pairs(ports)) == [("a", "b"), ("c", "d")]


def describe_within_direction_similarity():
    def it_carries_the_run_ids_and_the_condition_of_both_sides(cell, git_diff):
        frame = within_direction_similarity(cell)
        assert frame.height == 10
        assert frame.columns == [
            "run_id_a",
            "run_id_b",
            "source_language",
            "target_language",
            "include_python_tests_a",
            "include_typescript_tests_a",
            "include_python_tests_b",
            "include_typescript_tests_b",
            "similarity_pct",
        ]
        assert frame.row(0, named=True) == {
            "run_id_a": "run-0",
            "run_id_b": "run-1",
            "source_language": "python",
            "target_language": "typescript",
            "include_python_tests_a": False,
            "include_typescript_tests_a": False,
            "include_python_tests_b": False,
            "include_typescript_tests_b": False,
            "similarity_pct": 76.19,
        }

    def it_reads_each_side_of_a_cross_condition_pair_off_its_own_run(git_diff):
        frame = within_direction_similarity([StubPort("a"), StubPort("b", python_tests=True)])
        assert frame.row(0, named=True)["include_python_tests_a"] is False
        assert frame.row(0, named=True)["include_python_tests_b"] is True

    def it_runs_the_diff_once_per_pair(cell, git_diff):
        within_direction_similarity(cell)
        assert git_diff.call_count == 10

    def it_diffs_the_two_ports_under_the_target_language_and_the_excludes(cell, git_diff):
        within_direction_similarity(cell)
        first = git_diff.call_args_list[0]
        assert first.args == (cell[0].path, cell[1].path)
        assert first.kwargs == {
            "language": "typescript",
            "exclude": ["--exclude", "node_modules", "--exclude", "*_test.py"],
        }

    def it_has_no_rows_for_a_direction_of_one(git_diff):
        assert within_direction_similarity([StubPort("a")]).height == 0


def describe_within_cell():
    def it_keeps_the_pairs_whose_two_ports_share_a_condition(git_diff):
        ports = [StubPort("a"), StubPort("b"), StubPort("c", python_tests=True)]
        assert within_cell(within_direction_similarity(ports))["run_id_b"].to_list() == ["b"]

    def it_names_the_shared_condition_once(git_diff):
        frame = within_cell(within_direction_similarity([StubPort("a"), StubPort("b")]))
        assert frame.columns == [
            "run_id_a",
            "run_id_b",
            "source_language",
            "target_language",
            "include_python_tests",
            "include_typescript_tests",
            "similarity_pct",
        ]

    def it_pairs_every_run_in_a_cell_once(cell, git_diff):
        assert within_cell(within_direction_similarity(cell)).height == 10


CONDITIONS = [
    ("no tests", False, False),
    ("source tests", True, False),
    ("target tests", False, True),
    ("both tests", True, True),
]


def labelled_of(*ports):
    return label_conditions(within_direction_similarity(list(ports)), CONDITIONS)


def describe_label_conditions():
    def it_names_each_side_with_its_own_condition(git_diff):
        row = labelled_of(StubPort("a"), StubPort("b", python_tests=True)).row(0, named=True)
        assert row["condition_a"] == "no tests"
        assert row["condition_b"] == "source tests"

    def it_names_both_sides_alike_when_the_pair_shares_a_condition(git_diff):
        row = labelled_of(StubPort("a"), StubPort("b")).row(0, named=True)
        assert row["condition_a"] == row["condition_b"] == "no tests"

    def it_keeps_the_run_ids_and_the_similarity_of_the_pair(git_diff):
        row = labelled_of(StubPort("a"), StubPort("b")).row(0, named=True)
        assert (row["run_id_a"], row["run_id_b"]) == ("a", "b")
        assert row["similarity_pct"] == DIFF_REPORT["similarity_pct"]

    def it_has_no_rows_for_a_direction_of_one(git_diff):
        assert labelled_of(StubPort("a")).height == 0


REFERENCE_SIMILARITY = pl.DataFrame(
    {"run_id": ["a", "b"], "reference_similarity_pct": [61.0, 42.0]}
)


def describe_pairs_by_port():
    def it_reads_every_pair_from_each_port_in_turn(cell, git_diff):
        reference = pl.DataFrame(
            {
                "run_id": [port.run["run_id"] for port in cell],
                "reference_similarity_pct": [50.0] * len(cell),
            }
        )
        assert pairs_by_port(labelled_of(*cell), reference).height == 20

    def it_swaps_the_run_ids_and_the_conditions_together(git_diff):
        frame = pairs_by_port(
            labelled_of(StubPort("a"), StubPort("b", python_tests=True)), REFERENCE_SIMILARITY
        )
        assert frame["run_id_a"].to_list() == ["a", "b"]
        assert frame["run_id_b"].to_list() == ["b", "a"]
        assert frame["condition_a"].to_list() == ["no tests", "source tests"]
        assert frame["condition_b"].to_list() == ["source tests", "no tests"]

    def it_carries_the_reference_similarity_of_the_port_the_row_is_read_from(git_diff):
        frame = pairs_by_port(labelled_of(StubPort("a"), StubPort("b")), REFERENCE_SIMILARITY)
        assert frame["reference_similarity_pct"].to_list() == [61.0, 42.0]

    def it_measures_the_same_similarity_from_either_side(git_diff):
        frame = pairs_by_port(labelled_of(StubPort("a"), StubPort("b")), REFERENCE_SIMILARITY)
        assert frame["similarity_pct"].to_list() == [DIFF_REPORT["similarity_pct"]] * 2

    def it_drops_a_pair_read_from_a_port_with_no_reference_number(git_diff):
        reference = REFERENCE_SIMILARITY.head(1)
        frame = pairs_by_port(labelled_of(StubPort("a"), StubPort("b")), reference)
        assert frame["run_id_a"].to_list() == ["a"]
