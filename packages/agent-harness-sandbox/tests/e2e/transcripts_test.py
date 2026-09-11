"""Whether a session transcript survives the run that produced it.

`CLAUDE_CONFIG_DIR` is a staged per-run tempdir, so the session jsonl written
under it dies with it. Binding the caller's directory at the `projects` path is
what keeps it: a bind nested inside the staged `.claude` mount, written by the
non-root `node` user, neither of which a mocked docker can prove.
"""

import pytest

from agent_harness_sandbox import AgentHarnessSandboxError, run_agent_harness_sandbox

SLUG = "-workspace"


@pytest.fixture(scope="module")
def session(sandbox):
    return sandbox({"ok": "echo ok"})


def describe_transcripts():
    def it_lands_a_session_jsonl_on_the_host(session):
        assert list(session.transcripts.rglob("*.jsonl"))

    def it_files_the_session_under_the_workdir_it_ran_in(session):
        assert (session.transcripts / SLUG).is_dir()

    def it_refuses_a_missing_host_directory(options, tmp_path):
        """Refused before claude is ever invoked, so a typo costs nothing."""
        with pytest.raises(AgentHarnessSandboxError, match="does not exist"):
            run_agent_harness_sandbox("hi", **options(transcripts=tmp_path / "gone"))
