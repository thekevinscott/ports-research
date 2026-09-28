from pathlib import Path

from agent_harness_sandbox.agents.agent import Agent
from porting_harness.run_porting_harness import run_porting_harness
from .condition_name import condition_name
from .prepare_filesystem import PreparedFilesystem
from .render_prompt import LANGUAGE_DIRECTORIES, render_prompt

TARGET_LANGUAGES = {"typescript": "python", "python": "typescript"}


def run_gbnf_experiment(
    *,
    agent: Agent,
    source_language: str,
    include_unit_tests: bool,
    include_source_integration_tests: bool,
    include_target_integration_tests: bool,
    debug: bool,
    **kwargs,
) -> Path:
    with PreparedFilesystem(
        source_language=LANGUAGE_DIRECTORIES[source_language],
        include_unit_tests=include_unit_tests,
        include_source_integration_tests=include_source_integration_tests,
        include_target_integration_tests=include_target_integration_tests,
        debug=debug,
    ) as prepared_filesystem:
        target = TARGET_LANGUAGES[source_language]
        condition = dict(
            name=condition_name(
                source_language=source_language,
                include_unit_tests=include_unit_tests,
                include_source_integration_tests=include_source_integration_tests,
                include_target_integration_tests=include_target_integration_tests,
                **kwargs,
            ),
            source_language=source_language,
            target_language=target,
            include_unit_tests=include_unit_tests,
            include_source_integration_tests=include_source_integration_tests,
            include_target_integration_tests=include_target_integration_tests,
            **kwargs,
        )
        prompt = render_prompt(source_language=source_language, target_language=target)
        prepared_filesystem.write_manifest(agent, prompt=prompt, **condition)
        try:
            result = run_porting_harness(
                agent=agent,
                prompt=prompt,
                reference=prepared_filesystem.reference_directory,
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
            prepared_filesystem.write_result(
                stdout, agent, prompt=prompt, error=str(e), **condition
            )
            raise
        prepared_filesystem.write_result(result, agent, prompt=prompt, **condition)
        return prepared_filesystem.run_directory
