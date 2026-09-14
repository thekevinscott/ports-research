"""EVERY TEST IN THIS FILE INVOKES CLAUDE FOR REAL AND IS BILLED.

Each `ported(...)` call starts a real `claude -p` session against Kevin's credentials.
Runs with the rest of the tier under `just test-e2e`.

- Never re-run a failing test to chase green. A red one is a finding to report.
- One session per direction; the module-scoped cache enforces that. Do not make it
  function-scoped.
- The prompt is the harness's own — a caller cannot supply one, so there is nothing
  here to keep in step with it.
- Every assertion here is about the harness — what it returns and what it banks on the
  host. Whether the port is any good is an experiment result, graded elsewhere.
"""

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

import pytest
from agent_harness_sandbox import ClaudeAgent
from porting_harness import run_porting_harness

TARGET_LANGUAGE = {"typescript": "python", "python": "typescript"}

MODEL = "claude-opus-5"


@dataclass
class Port:
    """One live session: where its output landed and what claude reported about it."""

    directory: Path
    transcripts: Path
    proxy_log: Path
    raw: str = ""
    failure: Exception | None = None
    result: dict = field(default_factory=dict)

    def transcript_files(self) -> list[Path]:
        """The session jsonl the CLI wrote through agent-harness-sandbox's transcript mount, if any."""
        return list(self.transcripts.rglob("*.jsonl"))

    def summary(self) -> str:
        if self.failure is not None:
            return f"the session failed: {self.failure}"
        usage = self.result.get("usage") or {}
        return (
            f"turns={self.result.get('num_turns')}"
            f" input_tokens={usage.get('input_tokens')}"
            f" output_tokens={usage.get('output_tokens')}"
            f" cache_creation_input_tokens={usage.get('cache_creation_input_tokens')}"
            f" cache_read_input_tokens={usage.get('cache_read_input_tokens')}"
            f" duration_ms={self.result.get('duration_ms')}"
            f" is_error={self.result.get('is_error')}"
            f" session={self.result.get('session_id')}"
        )


@pytest.fixture(scope="module")
def ported(tmp_path_factory, two_number_adder: Path):
    """Port the fixture once per direction and hand the same result to every test."""
    sessions: dict[str, Port] = {}

    def port(source_language: str) -> Port:
        if source_language in sessions:
            return sessions[source_language]

        target_language = TARGET_LANGUAGE[source_language]
        root = tmp_path_factory.mktemp(f"{source_language}_to_{target_language}_")
        reference_implementation = root / "reference_implementation"
        shutil.copytree(
            two_number_adder / "source" / source_language,
            reference_implementation / "source",
        )
        shutil.copytree(
            two_number_adder / "tests" / target_language,
            reference_implementation / "tests" / target_language,
        )

        transcripts = root / "transcripts"
        transcripts.mkdir()
        session = Port(
            directory=root / "ported_implementation",
            transcripts=transcripts,
            proxy_log=root / "proxy.log",
        )
        sessions[source_language] = session
        try:
            session.raw = run_porting_harness(
                agent=ClaudeAgent(),
                reference_implementation=reference_implementation,
                target_language=target_language,
                output_directory=session.directory,
                debug=False,
                effort="high",
                model=MODEL,
                transcripts=session.transcripts,
                proxy_log=session.proxy_log,
            )
        except Exception as failure:  # noqa: BLE001
            session.failure = failure
        try:
            session.result = json.loads(session.raw)
        except (json.JSONDecodeError, TypeError):
            session.result = {}
        print(f"\n[live] {source_language} -> {target_language}: {session.summary()}")
        print(f"[live] port at {session.directory}")
        print(f"[live] transcript at {session.transcripts} ({len(session.transcript_files())} jsonl)")
        print(f"[live] claude said: {session.result.get('result', session.raw)}")
        return session

    return port


def describe_porting_typescript_to_python():
    def it_finishes_the_session(ported):
        session = ported("typescript")
        assert session.failure is None, session.failure
        assert session.result.get("is_error") is False, session.raw

    def it_captures_a_session_transcript(ported):
        session = ported("typescript")
        assert session.failure is None, session.failure
        captured = session.transcript_files()
        assert captured, f"no .jsonl transcript under {session.transcripts}"
        assert any(path.stat().st_size > 0 for path in captured), "the transcript is empty"

    def it_syncs_what_the_agent_wrote_into_the_output_directory(ported):
        session = ported("typescript")
        assert session.failure is None, session.failure
        written = [path for path in session.directory.rglob("*") if path.is_file()]
        assert written, f"nothing came back out of {session.directory}"

    def it_banks_the_proxy_denial_log_where_the_caller_asked(ported):
        session = ported("typescript")
        assert session.failure is None, session.failure
        assert session.proxy_log.is_file(), "the tinyproxy log died with the container"
        assert session.proxy_log.read_text().strip(), "the banked proxy log is empty"


def describe_porting_python_to_typescript():
    def it_finishes_the_session(ported):
        session = ported("python")
        assert session.failure is None, session.failure
        assert session.result.get("is_error") is False, session.raw

    def it_syncs_what_the_agent_wrote_into_the_output_directory(ported):
        session = ported("python")
        assert session.failure is None, session.failure
        written = [path for path in session.directory.rglob("*") if path.is_file()]
        assert written, f"nothing came back out of {session.directory}"
