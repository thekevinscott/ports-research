from pathlib import Path

from botbox import Agent
from port_codebase import port_codebase
from port_codebase.prompt import Prompt
from .condition_name import condition_name
from .prepare_filesystem import PreparedFilesystem
from .suites_information import suites_information

TARGET_LANGUAGES = {"javascript": "python", "python": "javascript"}
# Named in the prompt because the agent has no registry access to discover it.
PACKAGE_MANAGERS = {"python": "uv", "javascript": "pnpm"}
# The library half of the prompt. port_codebase frames the task; only this
# package knows how it laid the source directory out.
PROMPT_PATH = Path(__file__).parent / "prompt.txt"


def run_gbnf_experiment(
    *,
    agent: Agent,
    source_language: str,
    include_javascript_tests: bool,
    include_python_tests: bool,
    debug: bool,
) -> Path:
    with PreparedFilesystem(
        source_language=source_language,
        include_javascript_tests=include_javascript_tests,
        include_python_tests=include_python_tests,
        debug=debug,
    ) as prepared_filesystem:
        target = TARGET_LANGUAGES[source_language]
        condition = dict(
            name=condition_name(
                source_language=source_language,
                include_javascript_tests=include_javascript_tests,
                include_python_tests=include_python_tests,
                effort=agent.effort,
                model=agent.model,
            ),
            source_language=source_language,
            target_language=target,
            include_python_tests=include_python_tests,
            include_javascript_tests=include_javascript_tests,
            effort=agent.effort,
            model=agent.model,
        )
        prepared_filesystem.write_manifest(agent, **condition)
        try:
            result = port_codebase(
                agent=agent,
                prompt=str(
                    Prompt(
                        PROMPT_PATH,
                        target_language=target,
                        package_manager=PACKAGE_MANAGERS[target],
                        suites_information=suites_information(
                            include_javascript_tests=include_javascript_tests,
                            include_python_tests=include_python_tests,
                        ),
                    )
                ),
                source=prepared_filesystem.reference_implementation_directory,
                output=prepared_filesystem.ported_implementation_directory,
            )
        except Exception as e:
            prepared_filesystem.write_result(None, agent, error=str(e), **condition)
            raise
        for path, text in result.transcript.items():
            destination = prepared_filesystem.transcript_directory / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(text)
        prepared_filesystem.proxy_log.write_text(result.proxy)
        prepared_filesystem.write_result(result.stdout, agent, **condition)
        return prepared_filesystem.run_directory
