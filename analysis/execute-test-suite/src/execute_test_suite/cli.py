import json
import sys
from pathlib import Path

import click
from gbnf_experiment.config import prepare_cache_key, settings

from .execute_test_suite import execute_test_suite


@click.command()
@click.option(
    "--language",
    type=click.Choice(["python", "typescript", "javascript"]),
    required=True,
)
@click.option(
    "--target",
    type=click.Path(exists=True, file_okay=False, path_type=Path, resolve_path=True),
    required=True,
)
@click.option("--suite", type=click.Choice(["unit", "integration"]), default=None)
@click.option("--adapt", is_flag=True, default=False)
@click.option("--coverage", is_flag=True, default=False)
def cli(language: str, target: Path, suite: str | None, adapt: bool, coverage: bool) -> None:
    try:
        report = execute_test_suite(
            language=language,
            target=target,
            suite=suite,
            adapt=adapt,
            coverage=coverage,
            derivations_directory=settings.prepared_directory,
            derivation_cache_key=prepare_cache_key,
        )
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(json.dumps(report))
    sys.exit(0 if report["success"] else 1)
