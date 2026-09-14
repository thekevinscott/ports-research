from datetime import UTC, datetime
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Tuple
from agent_harness_sandbox import Agent
from ..config import settings, derivation_cache_key
from .assemble_reference_implementation import assemble_reference_implementation
from .prepare_reference_implementation import prepare_reference_implementation
from .run_directory_name import run_directory_name
from .write_manifest import write_manifest as _write_manifest

class PreparedFilesystem:
    def __init__(
        self,
        *,
        source_language: str,
        include_typescript_tests: bool,
        include_python_tests: bool,
        debug: bool,
    ):
        self.timestamp = datetime.now(UTC)
        self.derivation_directory = settings.derivations_directory / derivation_cache_key
        if not self.derivation_directory.exists():
            prepare_reference_implementation(
                output_directory=self.derivation_directory, 
                debug=debug,
            )
        self.run_directory = settings.data_directory / run_directory_name(self.timestamp)
        self.ported_implementation_directory = self.run_directory / "ported_implementation"
        self.ported_implementation_directory.mkdir(parents=True)
        self.transcript_directory = self.run_directory / "transcript"
        self.transcript_directory.mkdir()
        # Scratch, not run record: the container reads this tree read-only for the
        # length of the run, and it is reassembled from the derivation cache.
        self._reference_implementation_staging = TemporaryDirectory()
        self.reference_implementation_directory = assemble_reference_implementation(
            derivation_directory=self.derivation_directory,
            output_directory=Path(self._reference_implementation_staging.name)
            / "reference_implementation",
            source_language=source_language,
            include_typescript_tests=include_typescript_tests,
            include_python_tests=include_python_tests,
        )

    def __enter__(self):
        return self

    def __exit__(self, *exception):
        self._reference_implementation_staging.cleanup()
        return False

    @property
    def proxy_log(self):
        return self.run_directory / "proxy.log"


    def write_manifest(self, agent: Agent, **kwargs):
        _write_manifest(
            self.run_directory,
            timestamp=self.timestamp,
            condition={
                **kwargs,
            },
            image_tag=agent.image,
            gbnf_commit=settings.gbnf_commit,
            completed_at=None,
        )

    def write_result(
        self, result: str | None, agent: Agent, error: str | None = None, **kwargs
    ):
        if result:
            (self.run_directory / "result.json").write_text(result)
        _write_manifest(
            self.run_directory,
            timestamp=self.timestamp,
            condition={
                **kwargs,
            },
            image_tag=agent.image,
            gbnf_commit=settings.gbnf_commit,
            completed_at=datetime.now(UTC),
            error=error,
        )
