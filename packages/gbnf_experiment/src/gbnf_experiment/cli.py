import json
from pathlib import Path

import click

from botbox import ClaudeAgent

from gbnf_experiment import config
from gbnf_experiment.run_gbnf_experiment import run_gbnf_experiment

DEFAULT_MODEL = "claude-opus-5"
INCLUDE = click.Choice(["0", "1"])


def failure(run_directory: Path) -> str | None:
    manifest = json.loads((run_directory / "manifest.json").read_text())
    result_path = run_directory / "result.json"
    result = json.loads(result_path.read_text()) if result_path.is_file() else {}
    if manifest.get("exit_code") != 0:
        return f"the agent exited {manifest.get('exit_code')}"
    if result.get("is_error"):
        return "the agent's result is an error"
    if manifest.get("error") is not None:
        return manifest["error"]
    return None


@click.command()
@click.option(
    "--source-language",
    type=click.Choice(["javascript", "python"]),
    required=True,
)
@click.option("--include-unit-tests", type=INCLUDE, default="0")
@click.option("--include-source-integration-tests", type=INCLUDE, default="0")
@click.option("--include-target-integration-tests", type=INCLUDE, default="0")
@click.option("--debug", is_flag=True, default=False)
# Both free text: claude errors on an unknown model or effort instead of warning and running the default.
@click.option("--effort", default="high", show_default=True)
@click.option("--model", default=DEFAULT_MODEL, show_default=True)
def cli(
    source_language: str,
    include_unit_tests: str,
    include_source_integration_tests: str,
    include_target_integration_tests: str,
    debug: bool,
    effort: str,
    model: str,
) -> None:
    """One run, written into the working folder."""
    run_directory = Path.cwd()
    agent = ClaudeAgent(model=model, effort=effort, api_key=config.API_KEY or None)
    try:
        run_gbnf_experiment(
            agent=agent,
            run_directory=run_directory,
            source_language=source_language,
            include_unit_tests=include_unit_tests == "1",
            include_source_integration_tests=include_source_integration_tests == "1",
            include_target_integration_tests=include_target_integration_tests == "1",
            debug=debug,
        )
    except Exception as e:
        raise click.ClickException(str(e))
    if reason := failure(run_directory):
        raise click.ClickException(reason)
