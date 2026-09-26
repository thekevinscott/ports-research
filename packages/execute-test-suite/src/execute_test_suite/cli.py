import json
import sys
from pathlib import Path

import click

from .execute_test_suite import execute_test_suite


@click.command()
@click.option(
    "--language",
    type=click.Choice(["python", "typescript"]),
    required=True,
)
@click.option(
    "--target",
    type=click.Path(exists=True, file_okay=False, path_type=Path, resolve_path=True),
    required=True,
)
@click.option(
    "--test-suites",
    "test_suites_directory",
    type=click.Path(exists=True, file_okay=False, path_type=Path, resolve_path=True),
    required=True,
)
@click.option("--suite", type=click.Choice(["unit", "integration"]), default=None)
@click.option("--adapt", is_flag=True, default=False)
@click.option("--coverage", is_flag=True, default=False)
def cli(
    language: str,
    target: Path,
    test_suites_directory: Path,
    suite: str | None,
    adapt: bool,
    coverage: bool,
) -> None:
    try:
        report = execute_test_suite(
            language=language,
            target=target,
            test_suites_directory=test_suites_directory,
            suite=suite,
            adapt=adapt,
            coverage=coverage,
        )
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(json.dumps(report))
    sys.exit(0 if report["success"] else 1)
