import json
from pathlib import Path

import click

from .perturb_reference_tree import perturb_reference_tree


@click.command()
@click.option(
    "--source",
    type=click.Path(exists=True, file_okay=False, path_type=Path, resolve_path=True),
    required=True,
)
@click.option(
    "--output",
    type=click.Path(file_okay=False, path_type=Path, resolve_path=True),
    required=True,
)
@click.option("--library-name", required=True)
@click.option("--seed", type=int, default=0, show_default=True)
def cli(source: Path, output: Path, library_name: str, seed: int) -> None:
    try:
        new_library_name = perturb_reference_tree(
            source, output, library_name=library_name, seed=seed
        )
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(
        json.dumps({"output": str(output), "library_name": new_library_name, "seed": seed})
    )
