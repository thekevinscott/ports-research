from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from agent_harness_sandbox.agents.agent import Agent

from ..config import settings
from .included_files import included_files
from .prepare_reference_implementation import prepare_reference_implementation
from .run_directory_name import run_directory_name
from .write_manifest import write_manifest as _write_manifest


class PreparedFilesystem:
    def __init__(
        self,
        *,
        source_language: str,
        include_unit_tests: bool,
        include_source_integration_tests: bool,
        include_target_integration_tests: bool,
        debug: bool,
    ):
        self.timestamp = datetime.now(UTC)
        self.run_directory = settings.data_directory / run_directory_name(self.timestamp)
        self.ported_implementation_directory = self.run_directory / "ported_implementation"
        self.ported_implementation_directory.mkdir(parents=True)
        self.transcript_directory = self.run_directory / "transcript"
        self.transcript_directory.mkdir()
        # Scratch, not run record: the container reads this tree read-only for the
        # length of the run, and it is rebuildable from the pinned commit.
        self._reference_staging = TemporaryDirectory()
        self.reference_directory = prepare_reference_implementation(
            output_directory=Path(self._reference_staging.name),
            source_language=source_language,
            include_unit_tests=include_unit_tests,
            include_source_integration_tests=include_source_integration_tests,
            include_target_integration_tests=include_target_integration_tests,
            debug=debug,
        )
        self.included = included_files(self.reference_directory)

    def __enter__(self):
        return self

    def __exit__(self, *exception):
        self._reference_staging.cleanup()
        return False

    @property
    def proxy_log(self):
        return self.run_directory / "proxy.log"

    def write_manifest(self, agent: Agent, *, prompt: str, **kwargs):
        _write_manifest(
            self.run_directory,
            timestamp=self.timestamp,
            prompt=prompt,
            condition={
                **kwargs,
            },
            included=[path.as_posix() for path in self.included],
            image_tag=agent.image,
            gbnf_commit=settings.gbnf_commit,
            completed_at=None,
        )

    def write_result(
        self,
        result: str | None,
        agent: Agent,
        *,
        prompt: str,
        error: str | None = None,
        **kwargs,
    ):
        if result:
            (self.run_directory / "result.json").write_text(result)
        _write_manifest(
            self.run_directory,
            timestamp=self.timestamp,
            prompt=prompt,
            condition={
                **kwargs,
            },
            included=[path.as_posix() for path in self.included],
            image_tag=agent.image,
            gbnf_commit=settings.gbnf_commit,
            completed_at=datetime.now(UTC),
            error=error,
        )
