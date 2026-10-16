import json
from pathlib import Path

import pytest
from completed_runs import completed_runs
from conftest import git, write_design

STUDY = "v2-model-effort"
CELL = {"source_language": "python", "model": "claude-opus-5-5", "effort": "low"}


def bank(output: Path, name: str, commit: str | None, exit_code: int = 0) -> None:
    directory = output / name
    directory.mkdir(parents=True)
    manifest = {"study": STUDY, "condition": CELL, "exit_code": exit_code, "error": None, "completed_at": "2026-10-16"}
    if commit is not None:
        manifest["harness"] = {"commit": commit, "dirty": True}
    (directory / "manifest.json").write_text(json.dumps(manifest))
    (directory / "result.json").write_text(json.dumps({"is_error": False}))


def run_ids(output: Path, root: Path) -> list[str]:
    return sorted(run["run_id"] for run in completed_runs(output, STUDY, root=root))


def describe_completed_runs():
    @pytest.mark.parametrize(("commit", "counted"), [("since", True), ("after", True), ("before", False)])
    def it_counts_a_run_only_on_prompt_since_or_a_descendant(tmp_path, repo, commit, counted):
        root, commits = repo
        write_design(root, "models-effort", STUDY, commits["since"])
        output = tmp_path / "runs"
        bank(output, commit, commits[commit])
        assert run_ids(output, root) == ([commit] if counted else [])

    def it_does_not_count_a_run_without_a_harness_commit(tmp_path, repo):
        root, commits = repo
        write_design(root, "models-effort", STUDY, commits["since"])
        output = tmp_path / "runs"
        bank(output, "uncommitted", None)
        bank(output, "since", commits["since"])
        assert run_ids(output, root) == ["since"]

    def it_filters_by_the_design_s_completed_run_clause(tmp_path, repo):
        root, commits = repo
        write_design(root, "models-effort", STUDY, commits["since"], completed_run="exit_code = 3")
        output = tmp_path / "runs"
        bank(output, "zero", commits["since"])
        bank(output, "three", commits["since"], exit_code=3)
        assert run_ids(output, root) == ["three"]

    def it_raises_when_no_design_names_the_study(tmp_path, repo):
        root, commits = repo
        write_design(root, "other", "v2-other", commits["since"])
        bank(tmp_path / "runs", "since", commits["since"])
        with pytest.raises(ValueError, match=STUDY):
            completed_runs(tmp_path / "runs", STUDY, root=root)

    def it_raises_when_two_designs_name_the_study(tmp_path, repo):
        root, commits = repo
        write_design(root, "one", STUDY, commits["since"])
        write_design(root, "two", STUDY, commits["since"])
        bank(tmp_path / "runs", "since", commits["since"])
        with pytest.raises(ValueError, match=STUDY):
            completed_runs(tmp_path / "runs", STUDY, root=root)

    def it_counts_a_run_descending_from_any_prompt_since_in_a_list(tmp_path, repo):
        root, commits = repo
        git(root, "checkout", "-q", "-b", "twin", commits["before"])
        git(root, "commit", "-q", "--allow-empty", "-m", "twin")
        twin = git(root, "rev-parse", "HEAD")
        git(root, "commit", "-q", "--allow-empty", "-m", "after twin")
        output = tmp_path / "runs"
        bank(output, "after-twin", git(root, "rev-parse", "HEAD"))
        bank(output, "after", commits["after"])
        bank(output, "before", commits["before"])
        write_design(root, "models-effort", STUDY, [commits["since"], twin])
        assert run_ids(output, root) == ["after", "after-twin"]
