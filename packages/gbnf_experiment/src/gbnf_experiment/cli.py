import click

from botbox import ClaudeAgent

from gbnf_experiment.run_gbnf_experiment import run_gbnf_experiment

DEFAULT_MODEL = "claude-opus-5"

@click.command()
@click.option(
    "--source-language",
    type=click.Choice(["javascript", "python"]),
    required=True,
)
@click.option("--include-unit-tests", is_flag=True, default=False)
@click.option("--include-source-integration-tests", is_flag=True, default=False)
@click.option("--include-target-integration-tests", is_flag=True, default=False)
@click.option("--debug", is_flag=True, default=False)
# Both free text: claude errors on an unknown model or effort instead of warning and running the default.
@click.option("--effort", default="high", show_default=True)
@click.option("--model", default=DEFAULT_MODEL, show_default=True)
def cli(
    source_language: str,
    include_unit_tests: bool,
    include_source_integration_tests: bool,
    include_target_integration_tests: bool,
    debug: bool,
    effort: str,
    model: str,
) -> None:
    agent = ClaudeAgent(model=model, effort=effort)
    try:
        run_directory = run_gbnf_experiment(
            agent=agent,
            source_language=source_language,
            include_unit_tests=include_unit_tests,
            include_source_integration_tests=include_source_integration_tests,
            include_target_integration_tests=include_target_integration_tests,
            debug=debug,
        )
        click.echo(f"Run directory: {run_directory}")
    except Exception as e:
        raise click.ClickException(str(e))
