from datetime import UTC, datetime

from agent_harness_sandbox.agents.agent import Agent
from agent_harness_sandbox.build_agent_image import build_agent_image
from porting_harness.select_files import select_files

from ..config import settings
from .build_workspace_image import build_workspace_image
from .list_prepared_files import list_prepared_files
from .reference_patterns import reference_patterns
from .run_directory_name import run_directory_name
from .write_manifest import write_manifest as _write_manifest


class PreparedFilesystem:
    def __init__(
        self,
        *,
        agent: Agent,
        source_language: str,
        include_typescript_tests: bool,
        include_python_tests: bool,
        debug: bool,
    ):
        self.timestamp = datetime.now(UTC)
        self.included = select_files(
            paths=list_prepared_files(debug=debug),
            patterns=reference_patterns(
                source_language,
                include_typescript_tests=include_typescript_tests,
                include_python_tests=include_python_tests,
            ),
        )
        self.image = build_workspace_image(
            agent_image=build_agent_image(agent=agent, debug=debug),
            files=self.included,
            debug=debug,
        )
        self.run_directory = settings.data_directory / run_directory_name(self.timestamp)
        self.ported_implementation_directory = self.run_directory / "ported_implementation"
        self.ported_implementation_directory.mkdir(parents=True)
        self.transcript_directory = self.run_directory / "transcript"
        self.transcript_directory.mkdir()

    @property
    def proxy_log(self):
        return self.run_directory / "proxy.log"

    def write_manifest(self, **kwargs):
        _write_manifest(
            self.run_directory,
            timestamp=self.timestamp,
            condition={**kwargs},
            included=[path.as_posix() for path in self.included],
            image=self.image,
            gbnf_commit=settings.gbnf_commit,
            completed_at=None,
        )

    def write_result(self, result: str | None, error: str | None = None, **kwargs):
        if result:
            (self.run_directory / "result.json").write_text(result)
        _write_manifest(
            self.run_directory,
            timestamp=self.timestamp,
            condition={**kwargs},
            included=[path.as_posix() for path in self.included],
            image=self.image,
            gbnf_commit=settings.gbnf_commit,
            completed_at=datetime.now(UTC),
            error=error,
        )
