from datetime import UTC, datetime
from pathlib import Path

from botbox import Agent, RunResult

from gbnf_experiment import config
from gbnf_experiment.prepare_filesystem.prepare_reference_implementation import prepare_reference_implementation
from gbnf_experiment.prepare_filesystem.write_manifest import write_manifest as _write_manifest


class PreparedFilesystem:
    def __init__(
        self,
        *,
        source_language: str,
        include_unit_tests: bool,
        include_source_integration_tests: bool,
        include_target_integration_tests: bool,
        debug: bool,
        run_directory: Path,
    ):
        self.timestamp = datetime.now(UTC)
        # The extracted /shared, mounted as the agent's source as it is.
        self.reference_implementation_directory = prepare_reference_implementation(
            source_language=source_language,
            include_unit_tests=include_unit_tests,
            include_source_integration_tests=include_source_integration_tests,
            include_target_integration_tests=include_target_integration_tests,
            debug=debug,
        )
        self.included = sorted(
            path.relative_to(self.reference_implementation_directory).as_posix()
            for path in self.reference_implementation_directory.rglob("*")
            if path.is_file()
        )
        self.run_directory = run_directory
        self.ported_implementation_directory = self.run_directory / "ported_implementation"
        self.ported_implementation_directory.mkdir(parents=True)
        self.transcript_directory = self.run_directory / "transcript"
        self.transcript_directory.mkdir()
        self.result: RunResult | None = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.write_result(
            self.result,
            self.agent,
            error=None if exc_value is None else str(exc_value),
            **self.condition,
        )
        return False

    @property
    def proxy_log(self):
        return self.run_directory / "proxy.log"

    def write_manifest(self, agent: Agent, **kwargs):
        self.agent = agent
        self.condition = kwargs
        _write_manifest(
            self.run_directory,
            timestamp=self.timestamp,
            condition={
                **kwargs,
            },
            included=self.included,
            image_tag=agent.image,
            gbnf_commit=config.GBNF_COMMIT,
            completed_at=None,
        )

    def write_result(
        self, result: RunResult | None, agent: Agent, *, error: str | None = None, **kwargs
    ):
        if result is not None:
            if result.stdout:
                (self.run_directory / "result.json").write_text(result.stdout)
            (self.run_directory / "stderr.txt").write_text(result.stderr)
        _write_manifest(
            self.run_directory,
            timestamp=self.timestamp,
            condition={
                **kwargs,
            },
            included=self.included,
            image_tag=agent.image,
            gbnf_commit=config.GBNF_COMMIT,
            completed_at=datetime.now(UTC),
            exit_code=None if result is None else result.exit_code,
            error=error,
        )
