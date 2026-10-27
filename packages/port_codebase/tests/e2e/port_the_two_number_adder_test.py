"""EVERY TEST IN THIS FILE THAT CALLS `ported(...)` INVOKES CLAUDE FOR REAL AND IS BILLED.

Each `ported(...)` call starts a real `claude -p` session against Kevin's credentials.
Runs with the rest of the tier under `just test-e2e`.

- Never re-run a failing test to chase green. A red one is a finding to report.
- One session per direction; the module-scoped cache enforces that. Do not make it
  function-scoped.
- PROMPT below is this test's upstream prompt, describing the tree this test lays
  out. The harness appends it to its own system prompt. It stands in for an
  experiment's prompt and proves nothing about one.
- Every assertion here is about the harness — what it returns and what it leaves on the
  host. Whether the port is any good is an experiment result, graded elsewhere.
"""

import hashlib
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import pytest
from botbox import ClaudeAgent, RunResult

from port_codebase import port_codebase

TARGET_LANGUAGE = {"typescript": "python", "python": "typescript"}

MODEL = "claude-opus-5"
PROMPT = (
    "The library to port is in `source/`. Port it to {target_language}.\n"
    "The suite for the port is in `tests/`. Run it and iterate until green.\n"
)
ADMITTED = "api.anthropic.com"


def tree_hash(root: Path) -> str:
    """Every path under root and its bytes, in one digest."""
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        digest.update(path.relative_to(root).as_posix().encode())
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


@dataclass
class Port:
    """One live session: what went in, where the port landed, and what came back."""

    source: Path
    output: Path
    artifacts: Path
    source_hash_before: str
    output_existed_before: bool
    result: RunResult | None = None
    failure: Exception | None = None

    @property
    def stdout(self) -> str:
        return (self.artifacts / "stdout.txt").read_text()

    @property
    def stderr(self) -> str:
        return (self.artifacts / "stderr.txt").read_text()

    @property
    def transcripts(self) -> list[Path]:
        return list((self.artifacts / "transcripts").rglob("*.jsonl"))

    @property
    def proxy(self) -> str:
        return (self.artifacts / "proxy.log").read_text()

    def claude(self) -> dict:
        """Claude's JSON result, parsed from stdout."""
        assert self.failure is None, self.failure
        return json.loads(self.stdout)

    def summary(self) -> str:
        if self.failure is not None:
            return f"the session failed: {self.failure}"
        try:
            claude = json.loads(self.stdout)
        except json.JSONDecodeError:
            return f"exit_code={self.result.exit_code} stdout is not JSON"
        usage = claude.get("usage") or {}
        return (
            f"exit_code={self.result.exit_code}"
            f" turns={claude.get('num_turns')}"
            f" input_tokens={usage.get('input_tokens')}"
            f" output_tokens={usage.get('output_tokens')}"
            f" cache_creation_input_tokens={usage.get('cache_creation_input_tokens')}"
            f" cache_read_input_tokens={usage.get('cache_read_input_tokens')}"
            f" duration_ms={claude.get('duration_ms')}"
            f" is_error={claude.get('is_error')}"
            f" session={claude.get('session_id')}"
        )


@pytest.fixture(scope="module")
def ported(tmp_path_factory, two_number_adder: Path):
    """Port the fixture once per direction and hand the same result to every test."""
    sessions: dict[str, Port] = {}

    async def port(source_language: str) -> Port:
        if source_language in sessions:
            return sessions[source_language]

        target_language = TARGET_LANGUAGE[source_language]
        root = tmp_path_factory.mktemp(f"{source_language}_to_{target_language}_")
        source = root / "source"
        shutil.copytree(two_number_adder / "source" / source_language, source / "source")
        shutil.copytree(two_number_adder / "tests" / target_language, source / "tests")
        output = root / "output"

        session = Port(
            source=source,
            output=output,
            artifacts=root / "artifacts",
            source_hash_before=tree_hash(source),
            output_existed_before=output.exists(),
        )
        sessions[source_language] = session
        try:
            session.result = await port_codebase(
                agent=ClaudeAgent(model=MODEL, effort="high"),
                prompt=PROMPT.format(target_language=target_language),
                source=source,
                output=output,
                artifacts=session.artifacts,
            )
        except Exception as failure:  # noqa: BLE001
            session.failure = failure
        print(f"\n[live] {source_language} -> {target_language}: {session.summary()}")
        print(f"[live] port at {session.output}")
        if session.result is not None:
            print(f"[live] transcript files: {session.transcripts}")
            print(f"[live] stderr: {session.stderr}")
            print(f"[live] stdout: {session.stdout[:2000]}")
        return session

    return port


def proxied_hosts(log: str) -> tuple[set[str], set[str], set[str]]:
    """The hosts the proxy log names as requested, connected to, and refused."""
    requested = set(re.findall(r"CONNECT ([^\s:]+):\d+", log))
    connected = set(re.findall(r'Established connection to host "([^"]+)"', log))
    refused = set(re.findall(r'refused on filtered domain "([^"]+)"', log))
    return requested, connected, refused


@pytest.mark.parametrize("source_language", ["typescript", "python"])
def describe_porting_the_two_number_adder():
    async def it_exits_cleanly(ported, source_language):
        session = await ported(source_language)
        assert session.failure is None, session.failure
        assert session.result.exit_code == 0, session.stderr

    async def it_finishes_the_session(ported, source_language):
        assert (await ported(source_language)).claude()["is_error"] is False

    async def it_returns_a_session_transcript(ported, source_language):
        session = await ported(source_language)
        assert session.failure is None, session.failure
        sessions = [path for path in session.transcripts if path.stat().st_size]
        assert sessions, f"no non-empty .jsonl in {session.transcripts}"

    async def it_keeps_the_transcript_in_the_artifact_directory(ported, source_language):
        session = await ported(source_language)
        assert session.failure is None, session.failure
        assert session.transcripts
        assert all(path.is_relative_to(session.artifacts / "transcripts") for path in session.transcripts)

    async def it_returns_the_proxy_log(ported, source_language):
        session = await ported(source_language)
        assert session.failure is None, session.failure
        assert session.proxy.strip(), "the proxy log is empty"

    async def it_admits_only_the_anthropic_api(ported, source_language):
        session = await ported(source_language)
        assert session.failure is None, session.failure
        requested, connected, refused = proxied_hosts(session.proxy)
        assert connected == {ADMITTED}, session.proxy
        assert requested - {ADMITTED} <= refused, session.proxy

    async def it_creates_the_output(ported, source_language):
        session = await ported(source_language)
        assert session.output_existed_before is False
        assert session.output.is_dir()

    async def it_leaves_the_port_in_the_output(ported, source_language):
        session = await ported(source_language)
        assert session.failure is None, session.failure
        written = [p for p in session.output.rglob("*") if p.is_file()]
        assert written, f"nothing came back out of {session.output}"

    async def it_leaves_the_port_owned_by_the_host_user(ported, source_language):
        session = await ported(source_language)
        assert session.failure is None, session.failure
        owners = {p.stat().st_uid for p in session.output.rglob("*")}
        assert owners == {os.getuid()}

    async def it_leaves_the_source_untouched(ported, source_language):
        session = await ported(source_language)
        assert session.failure is None, session.failure
        assert tree_hash(session.source) == session.source_hash_before


def describe_a_missing_source():
    """Free: raises before any container starts, so no session is billed."""

    async def it_raises_and_creates_no_output(tmp_path):
        output = tmp_path / "output"

        with pytest.raises(FileNotFoundError):
            await port_codebase(
                agent=ClaudeAgent(model=MODEL, effort="high"),
                prompt="Port it.",
                source=tmp_path / "missing",
                output=output,
                artifacts=tmp_path / "artifacts",
            )

        assert not output.exists()
