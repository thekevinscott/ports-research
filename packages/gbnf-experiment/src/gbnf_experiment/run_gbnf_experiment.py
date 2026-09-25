from pathlib import Path

from agent_harness_sandbox.agents.agent import Agent
from porting_harness.run_porting_harness import run_porting_harness
from .condition_name import condition_name
from .prepare_filesystem import PreparedFilesystem

TARGET_LANGUAGES = {"typescript": "python", "python": "typescript"}


def run_gbnf_experiment(
    *,
    agent: Agent,
    source_language: str,
    include_typescript_tests: bool,
    include_python_tests: bool,
    debug: bool,
    **kwargs,
) -> Path:
    prepared_filesystem = PreparedFilesystem(
        agent=agent,
        source_language=source_language,
        include_typescript_tests=include_typescript_tests,
        include_python_tests=include_python_tests,
        debug=debug,
    )
    target = TARGET_LANGUAGES[source_language]
    condition = dict(
        name=condition_name(
            source_language=source_language,
            include_typescript_tests=include_typescript_tests,
            include_python_tests=include_python_tests,
            **kwargs,
        ),
        source_language=source_language,
        target_language=target,
        include_python_tests=include_python_tests,
        include_typescript_tests=include_typescript_tests,
        **kwargs,
    )
    prepared_filesystem.write_manifest(**condition)
    try:
        result = run_porting_harness(
            agent=agent,
            image=prepared_filesystem.image,
            target_language=target,
            output_directory=prepared_filesystem.ported_implementation_directory,
            debug=debug,
            **kwargs,
            transcripts=prepared_filesystem.transcript_directory,
            proxy_log=prepared_filesystem.proxy_log,
        )
    except Exception as e:
        # python_on_whales' DockerException carries the container's stdout: on a
        # non-zero exit that is still the agent's result JSON.
        stdout = getattr(e, "stdout", None)
        prepared_filesystem.write_result(stdout, error=str(e), **condition)
        raise
    prepared_filesystem.write_result(result, **condition)
    return prepared_filesystem.run_directory
