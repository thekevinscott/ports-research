from pathlib import Path
from unittest.mock import patch

import pytest

from round_trip_experiment.measure_git_diff import measure_git_diff

STATS = {"insertions": 3, "deletions": 1, "modified": 0, "renamed": 1, "added": 1, "deleted": 1}
FIELDS = {
    "language",
    "a",
    "b",
    "insertions",
    "deletions",
    "reference_lines",
    "diff_ratio",
    "similarity_pct",
    "identical",
    "modified",
    "renamed",
    "added",
    "deleted",
    "formatter_failures",
}


def write_tree(root: Path, files: dict[str, str]) -> Path:
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return root


@pytest.fixture
def stats():
    with patch("round_trip_experiment.measure_git_diff.git_diff_stats", autospec=True) as m:
        m.return_value = dict(STATS)
        yield m


@pytest.fixture
def a(tmp_path):
    return write_tree(tmp_path / "a", {"pkg/m.py": "x = 1\n", "pkg/n.py": "y = 2\n"})


@pytest.fixture
def b(tmp_path):
    return write_tree(tmp_path / "b", {"pkg/m.py": "x = 1\n", "pkg/o.py": "z = 3\n"})


def measure(a, b, exclude=[]):
    return measure_git_diff(language="python", a=a, b=b, exclude=exclude)


def describe_measure_git_diff():
    def it_reports_every_field(stats, a, b):
        assert set(measure(a, b)) == FIELDS

    def it_echoes_language_and_both_paths(stats, a, b):
        report = measure(a, b)
        assert (report["language"], report["a"], report["b"]) == ("python", str(a), str(b))

    def it_passes_git_the_two_normalized_copies_not_the_originals(stats, a, b):
        measure(a, b)
        left, right = stats.call_args.args
        assert (left.name, right.name) == ("a", "b")
        assert a not in left.parents and b not in right.parents

    def it_normalizes_under_the_shared_scratch_root(stats, a, b):
        measure(a, b)
        assert str(stats.call_args.args[0]).startswith("/tmp/claude/")

    def it_leaves_no_scratch_directory_behind(stats, a, b):
        measure(a, b)
        assert not stats.call_args.args[0].exists()

    def it_reports_the_counts_git_gave_it(stats, a, b):
        report = measure(a, b)
        assert {field: report[field] for field in STATS} == STATS

    def it_counts_the_normalized_lines_of_the_reference_side(stats, a, b):
        assert measure(a, b)["reference_lines"] == 2

    def it_divides_the_churn_by_the_reference_lines(stats, a, b):
        assert measure(a, b)["diff_ratio"] == pytest.approx(4 / 2)

    def it_counts_files_at_the_same_path_that_git_never_reported_as_identical(stats, a, b):
        assert measure(a, b)["identical"] == 1

    def it_does_not_count_a_modified_file_as_identical(stats, a, b):
        stats.return_value = {**STATS, "modified": 1}
        assert measure(a, b)["identical"] == 0

    def it_is_zero_and_all_identical_for_a_tree_against_itself(stats, a):
        stats.return_value = dict.fromkeys(STATS, 0)
        report = measure(a, a)
        assert (report["diff_ratio"], report["identical"]) == (0.0, 2)

    def it_scores_a_tree_against_itself_a_hundred_percent_similar(stats, a):
        stats.return_value = dict.fromkeys(STATS, 0)
        assert measure(a, a)["similarity_pct"] == 100.0

    def it_takes_the_similarity_as_dice_over_the_two_line_counts(stats, a, b):
        # shared 1 of the reference's 2 lines, so the port has 1 + 3 inserted.
        assert measure(a, b)["similarity_pct"] == pytest.approx(100 * 2 * 1 / (2 + 4))

    def it_scores_nothing_similar_when_every_reference_line_is_deleted(stats, a, b):
        stats.return_value = {**STATS, "insertions": 0, "deletions": 2}
        assert measure(a, b)["similarity_pct"] == 0.0

    def it_has_no_similarity_when_neither_side_has_a_line(stats, tmp_path):
        a = write_tree(tmp_path / "a", {"m.py": "# note\n"})
        b = write_tree(tmp_path / "b", {"m.py": "# other\n"})
        stats.return_value = dict.fromkeys(STATS, 0)
        assert measure(a, b)["similarity_pct"] is None

    def it_honours_the_excludes_on_both_sides(stats, tmp_path):
        a = write_tree(tmp_path / "a", {"m.py": "x = 1\n", "m_test.py": "z = 3\n"})
        b = write_tree(tmp_path / "b", {"m.py": "x = 1\n"})
        assert measure(a, b, exclude=["*_test.py"])["reference_lines"] == 1

    def it_labels_each_formatter_failure_with_its_side(stats, tmp_path, b):
        a = write_tree(tmp_path / "a", {"m.py": "x = 1\n", "bad.py": "def (:\n"})
        assert measure(a, b)["formatter_failures"] == [{"side": "a", "path": "bad.py"}]

    def it_raises_when_a_side_has_no_source_files(stats, a, tmp_path):
        empty = write_tree(tmp_path / "empty", {"notes.md": "not code"})
        with pytest.raises(FileNotFoundError, match="no python source"):
            measure(a, empty)
