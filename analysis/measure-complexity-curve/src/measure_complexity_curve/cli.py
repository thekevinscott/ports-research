import json
import sys
from pathlib import Path

import click

from .run_complexity_curve import run_complexity_curve


@click.command()
@click.option("--language", type=click.Choice(["python", "typescript"]), required=True)
@click.option(
    "--target",
    type=click.Path(exists=True, file_okay=False, path_type=Path, resolve_path=True),
    required=True,
)
@click.option("--max-size", type=int, default=128, show_default=True)
@click.option("--steps", type=int, default=6, show_default=True)
@click.option(
    "--nesting-depth",
    type=int,
    default=1,
    show_default=True,
    help="Kevin's python reference recurses to a RecursionError above 1 — see generate_grammar.py.",
)
@click.option("--alternation-width", type=int, default=3, show_default=True)
@click.option("--iterations", type=int, default=25, show_default=True)
@click.option("--seed", type=int, default=0, show_default=True)
def cli(
    language: str,
    target: Path,
    max_size: int,
    steps: int,
    nesting_depth: int,
    alternation_width: int,
    iterations: int,
    seed: int,
) -> None:
    try:
        report = run_complexity_curve(
            language=language,
            target=target,
            max_size=max_size,
            steps=steps,
            nesting_depth=nesting_depth,
            alternation_width=alternation_width,
            iterations=iterations,
            seed=seed,
        )
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(json.dumps(report))
    sys.exit(0)
