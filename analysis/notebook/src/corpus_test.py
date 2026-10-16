import json
import subprocess
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.Codebase import REFERENCE_CHECKOUT
from src.corpus import codebases_under, runs_under
from src.run_table import runs_table

V2_CONDITION = {
    "name": "source-python_unit-tests_effort-medium_model-claude-opus-5-5",
    "source_language": "python",
    "target_language": "javascript",
    "include_unit_tests": True,
    "include_source_integration_tests": False,
    "include_target_integration_tests": False,
    "effort": "medium",
    "model": "claude-opus-5-5",
}


STUDY = "v2-test-configurations"


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def commit(repo):
    git(repo, "commit", "-q", "--allow-empty", "-m", "c")
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture
def design(tmp_path):
    repo = tmp_path / "repo"
    (repo / "experiments" / "tests").mkdir(parents=True)
    git(repo, "init", "-q")
    before, since, after = commit(repo), commit(repo), commit(repo)
    (repo / "experiments" / "tests" / "design.yaml").write_text(
        f"study: {STUDY}\nruns_per_cell: 2\nprompt_since: '{since[:7]}'\n"
        "varies:\n  include_unit_tests: [false, true]\n"
    )
    return SimpleNamespace(repo=repo, before=before, since=since, after=after)


@pytest.fixture
def runs(tmp_path):
    runs = tmp_path / "runs"
    runs.mkdir()
    return runs


def write_v2_run(run_dir, harness_commit, exit_code=0, study=STUDY, completed_at="2026-10-12T09:56:41Z", **condition):
    (run_dir / "ported_implementation" / "src").mkdir(parents=True)
    (run_dir / "ported_implementation" / "src" / "index.ts").write_text("export default 1;\n")
    manifest = {
        "timestamp": "2026-10-12T09:49:53Z",
        "completed_at": completed_at,
        "exit_code": exit_code,
        "study": study,
        "condition": {**V2_CONDITION, **condition},
        "harness": {"commit": harness_commit, "dirty": False},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest))
    # A run killed with exit 137 never writes its result.
    if exit_code != 137:
        (run_dir / "result.json").write_text(json.dumps({"is_error": False, "duration_ms": 1}))


V1_CONDITION = {
    "source_language": "python",
    "target_language": "typescript",
    "include_python_tests": True,
    "include_typescript_tests": False,
    "effort": "medium",
    "model": "claude-opus-5-5",
}


def write_v1_run(run_dir):
    run_dir.mkdir(parents=True)
    manifest = {
        "timestamp": "2026-09-08T23:42:47Z",
        "completed_at": "2026-09-08T23:50:00Z",
        "condition": V1_CONDITION,
        "harness": {"commit": "353d5b3", "dirty": False},
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest))
    (run_dir / "result.json").write_text(json.dumps({"is_error": False, "duration_ms": 1}))


def run_ids(runs):
    return [run["run_id"] for run in runs]


@pytest.fixture
def pinned_reference():
    with patch("src.corpus.pinned_reference", autospec=True) as m:
        m.return_value = REFERENCE_CHECKOUT
        yield m


def describe_codebases_under():
    def it_builds_a_codebase_for_a_javascript_port(runs, design, pinned_reference):
        write_v2_run(runs / "20261012T094953Z_370ab98a", design.since)
        (codebase,) = codebases_under(runs, runs_table(), STUDY, repo=design.repo)
        assert codebase.language == "javascript"
        assert codebase.file_count == 1

    def it_measures_a_javascript_port_against_the_pinned_javascript_reference(runs, design, pinned_reference):
        write_v2_run(runs / "20261012T094953Z_370ab98a", design.since)
        (codebase,) = codebases_under(runs, runs_table(), STUDY, repo=design.repo)
        pinned_reference.assert_called_once_with()
        assert codebase.reference == REFERENCE_CHECKOUT / "packages" / "gbnf" / "javascript"

    def it_leaves_the_javascript_build_tooling_out_as_for_typescript(runs, design, pinned_reference):
        write_v2_run(runs / "20261012T094953Z_370ab98a", design.since)
        (codebase,) = codebases_under(runs, runs_table(), STUDY, repo=design.repo)
        assert {"builder", "dev"} <= set(codebase.exclude)

    def it_keeps_only_the_v2_codebases_of_the_named_study(runs, design, pinned_reference):
        write_v2_run(runs / "effort", design.since, study="v2-model-effort")
        write_v2_run(runs / "tests", design.since)
        assert [codebase.run_id for codebase in codebases_under(runs, runs_table(), STUDY, repo=design.repo)] == ["tests"]


def describe_runs_under():
    def it_lists_exit_zero_runs(runs, design):
        write_v2_run(runs / "ok", design.since)
        write_v2_run(runs / "killed", design.since, exit_code=137)
        assert run_ids(runs_under(runs, runs_table(), STUDY, repo=design.repo)) == ["ok"]

    def it_still_lists_failed_runs_when_asked(runs, design):
        write_v2_run(runs / "ok", design.since)
        write_v2_run(runs / "killed", design.since, exit_code=137)
        selected = runs_under(runs, runs_table(), STUDY, include_nonzero_exit=True, repo=design.repo)
        assert [(run["run_id"], run["exit_code"]) for run in selected] == [("killed", 137), ("ok", 0)]

    def it_keeps_only_the_v2_runs_of_the_named_study(runs, design):
        write_v2_run(runs / "effort", design.since, study="v2-model-effort")
        write_v2_run(runs / "tests", design.since)
        assert run_ids(runs_under(runs, runs_table(), STUDY, repo=design.repo)) == ["tests"]

    def it_keeps_v1_runs_regardless_of_the_design(runs, design):
        write_v1_run(runs / "v1")
        write_v2_run(runs / "effort", design.since, study="v2-model-effort")
        assert run_ids(runs_under(runs, runs_table(), STUDY, repo=design.repo)) == ["v1"]

    def it_drops_a_v2_run_whose_manifest_names_no_study(runs, design):
        write_v2_run(runs / "pilot", design.since, study=None)
        assert runs_under(runs, runs_table(), STUDY, repo=design.repo) == []

    def it_excludes_a_run_on_an_ancestor_of_prompt_since(runs, design):
        write_v2_run(runs / "before", design.before)
        write_v2_run(runs / "since", design.since)
        write_v2_run(runs / "after", design.after)
        assert run_ids(runs_under(runs, runs_table(), STUDY, repo=design.repo)) == ["after", "since"]

    def it_keeps_the_earliest_runs_per_cell_of_each_cell_by_completed_at(runs, design):
        write_v2_run(runs / "a", design.since, completed_at="2026-10-12T03:00:00Z")
        write_v2_run(runs / "b", design.since, completed_at="2026-10-12T01:00:00Z")
        write_v2_run(runs / "c", design.since, completed_at="2026-10-12T02:00:00Z")
        write_v2_run(runs / "d", design.since, source_language="javascript", completed_at="2026-10-12T04:00:00Z")
        write_v2_run(runs / "e", design.since, include_unit_tests=False, completed_at="2026-10-12T05:00:00Z")
        assert run_ids(runs_under(runs, runs_table(), STUDY, repo=design.repo)) == ["b", "c", "d", "e"]

    def it_does_not_count_failed_runs_against_the_cap(runs, design):
        write_v2_run(runs / "a", design.since, exit_code=1, completed_at="2026-10-12T01:00:00Z")
        write_v2_run(runs / "b", design.since, completed_at="2026-10-12T02:00:00Z")
        write_v2_run(runs / "c", design.since, completed_at="2026-10-12T03:00:00Z")
        selected = runs_under(runs, runs_table(), STUDY, include_nonzero_exit=True, repo=design.repo)
        assert run_ids(selected) == ["a", "b", "c"]

    def it_raises_when_no_design_names_the_study(runs, design):
        with pytest.raises(ValueError, match="v2-unknown"):
            runs_under(runs, runs_table(), "v2-unknown", repo=design.repo)
