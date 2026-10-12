import json
from pathlib import Path

import click

from measure_transcript.measure_transcript import measure_transcript


@click.command()
@click.option("--run", type=click.Path(exists=True, file_okay=False, path_type=Path, resolve_path=True), required=True)
def cli(run: Path) -> None:
    """Print the mechanical transcript measures of one run directory as JSON."""
    try:
        report = measure_transcript(run)
    except (FileNotFoundError, ValueError) as e:
        raise click.ClickException(str(e))
    click.echo(json.dumps(report))
