import json
from pathlib import Path

from botbox import Agent
from port_codebase import port_codebase
from prompt import Prompt
from gbnf_experiment.condition_name import condition_name
from gbnf_experiment.prepare_filesystem import PreparedFilesystem
from gbnf_experiment.suites_information import LANGUAGE_NAMES, suites_information

TARGET_LANGUAGES = {"javascript": "python", "python": "javascript"}
# The library half of the prompt. port_codebase frames the task; only this
# package knows how it laid the source directory out.
PROMPT_PATH = Path(__file__).parent / "prompts" / "prompt.txt"


class AgentFailed(Exception):
    pass


def run_gbnf_experiment(
    *,
    agent: Agent,
    run_directory: Path,
    source_language: str,
    include_unit_tests: bool,
    include_source_integration_tests: bool,
    include_target_integration_tests: bool,
    debug: bool,
) -> None:
    tests = dict(
        include_unit_tests=include_unit_tests,
        include_source_integration_tests=include_source_integration_tests,
        include_target_integration_tests=include_target_integration_tests,
    )
    prepared_filesystem = PreparedFilesystem(
        source_language=source_language, **tests, debug=debug, run_directory=run_directory
    )
    target = TARGET_LANGUAGES[source_language]
    condition = dict(
        name=condition_name(
            source_language=source_language,
            **tests,
            effort=agent.effort,
            model=agent.model,
        ),
        source_language=source_language,
        target_language=target,
        **tests,
        effort=agent.effort,
        model=agent.model,
    )
    with prepared_filesystem.recording(agent, **condition) as run:
        result = run.result = port_codebase(
            agent=agent,
            prompt=str(
                Prompt(
                    PROMPT_PATH,
                    source_language=source_language,
                    target_language=LANGUAGE_NAMES[target],
                    suites_information=suites_information(
                        source_language=source_language, **tests
                    ),
                )
            ),
            source=prepared_filesystem.reference_implementation_directory,
            output=prepared_filesystem.ported_implementation_directory,
        )
        for path, text in result.transcript.items():
            destination = prepared_filesystem.transcript_directory / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(text)
        prepared_filesystem.proxy_log.write_text(result.proxy)
        report = json.loads(result.stdout) if result.stdout else {}
        if report.get("is_error") or result.exit_code != 0:
            raise AgentFailed(report.get("result", f"the agent exited {result.exit_code}"))
