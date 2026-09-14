from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from round_trip_experiment.git_diff_stats import git_diff_stats

NUMSTAT = "3\t1\ta/pkg/m.py\n0\t2\ta/pkg/gone.py\n5\t0\t/dev/null => b/pkg/new.py\n0\t0\ta/pkg/n.py => b/pkg/renamed.py\n"
NAME_STATUS = "\0".join(
    ["M", "a/pkg/m.py", "D", "a/pkg/gone.py", "A", "b/pkg/new.py", "R100", "a/pkg/n.py", "b/pkg/renamed.py", ""]
)


def respond(numstat=NUMSTAT, name_status=NAME_STATUS, returncode=1):
    def run(argv, **kwargs):
        stdout = numstat if "--numstat" in argv else name_status
        return Mock(returncode=returncode, stdout=stdout, stderr="")

    return run


@pytest.fixture
def git():
    with patch("round_trip_experiment.git_diff_stats.subprocess", autospec=True) as m:
        m.run.side_effect = respond()
        yield m


def describe_git_diff_stats():
    def it_sums_insertions_and_deletions_over_every_numstat_row(git):
        stats = git_diff_stats(Path("/a"), Path("/b"))
        assert (stats["insertions"], stats["deletions"]) == (8, 3)

    def it_counts_each_name_status_letter(git):
        stats = git_diff_stats(Path("/a"), Path("/b"))
        assert (stats["modified"], stats["renamed"], stats["added"], stats["deleted"]) == (1, 1, 1, 1)

    def it_asks_git_for_rename_detection_without_an_index(git):
        git_diff_stats(Path("/a"), Path("/b"))
        for call in git.run.call_args_list:
            assert call.args[0][:4] == ["git", "diff", "--no-index", "-M"]

    def it_passes_both_directories_last_in_order(git):
        git_diff_stats(Path("/a"), Path("/b"))
        for call in git.run.call_args_list:
            assert call.args[0][-2:] == ["/a", "/b"]

    def it_reports_zeros_when_git_finds_no_difference(git):
        git.run.side_effect = respond(numstat="", name_status="", returncode=0)
        assert git_diff_stats(Path("/a"), Path("/b")) == {
            "insertions": 0,
            "deletions": 0,
            "modified": 0,
            "renamed": 0,
            "added": 0,
            "deleted": 0,
        }

    def it_counts_a_binary_file_as_no_lines(git):
        git.run.side_effect = respond(numstat="-\t-\ta/logo.png\n", name_status="\0".join(["M", "a/logo.png", ""]))
        stats = git_diff_stats(Path("/a"), Path("/b"))
        assert (stats["insertions"], stats["deletions"], stats["modified"]) == (0, 0, 1)

    def it_raises_when_git_itself_fails(git):
        git.run.side_effect = respond(returncode=128)
        with pytest.raises(RuntimeError, match="128"):
            git_diff_stats(Path("/a"), Path("/b"))
