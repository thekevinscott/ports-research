import asyncio
from pathlib import Path

import click
from dotenv import dotenv_values

from botbox import ClaudeAgent

from gbnf_experiment import config
from gbnf_experiment.run_gbnf_experiment import run_gbnf_experiment

DEFAULT_MODEL = "claude-opus-5"
INCLUDE = click.Choice(["0", "1"])


@click.command()
@click.option(
    "--source-language",
    type=click.Choice(["javascript", "python"]),
    required=True,
)
@click.option("--include-unit-tests", type=INCLUDE, default="0")
@click.option("--include-source-integration-tests", type=INCLUDE, default="0")
@click.option("--include-target-integration-tests", type=INCLUDE, default="0")
@click.option(
    "--output",
    type=click.Path(file_okay=False, path_type=Path),
    required=True,
    help="The run folder itself; created if missing.",
)
@click.option("--debug", is_flag=True, default=False)
# Both free text: claude errors on an unknown model or effort instead of warning and running the default.
@click.option("--effort", default="high", show_default=True)
@click.option("--model", default=DEFAULT_MODEL, show_default=True)
@click.option("--auth", type=click.Choice(["subscription", "api"]), default="subscription")
@click.option("--memory", default="8g", show_default=True, help="The agent container's memory cap, in Docker's size format.")
def cli(
    source_language: str,
    include_unit_tests: str,
    include_source_integration_tests: str,
    include_target_integration_tests: str,
    output: Path,
    debug: bool,
    effort: str,
    model: str,
    auth: str,
    memory: str,
) -> None:
    """One run, written into --output."""
    click.echo(f"*** auth: {auth} ***")
    api_key = None
    if auth == "api":
        env_path = config.REPO_ROOT / ".env"
        if not env_path.is_file():
            raise click.ClickException(f"Missing {env_path}; ANTHROPIC_API_KEY is required for --auth api")
        api_key = dotenv_values(env_path, interpolate=False).get("ANTHROPIC_API_KEY")
        if not api_key or not api_key.strip():
            raise click.ClickException(f"Missing or blank ANTHROPIC_API_KEY in {env_path}")
    run_directory = output.resolve()
    run_directory.mkdir(parents=True, exist_ok=True)
    agent = ClaudeAgent(model=model, effort=effort, api_key=api_key)
    asyncio.run(
        run_gbnf_experiment(
            agent=agent,
            run_directory=run_directory,
            source_language=source_language,
            include_unit_tests=include_unit_tests == "1",
            include_source_integration_tests=include_source_integration_tests == "1",
            include_target_integration_tests=include_target_integration_tests == "1",
            debug=debug,
            memory=memory,
        )
    )
