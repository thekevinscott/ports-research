import json
import subprocess
from pathlib import Path

import click
from gbnf_experiment.config import PACKAGE_ROOT as GBNF_EXPERIMENT_ROOT

from round_trip_experiment.cache_directories import prepared_directory, staging_directory
from round_trip_experiment.derivation_cache_key import derivation_cache_key
from round_trip_experiment.load_run import load_run
from round_trip_experiment.record_forward import record_forward
from round_trip_experiment.reverse_leg import reverse_leg
from round_trip_experiment.reverse_run_directory import reverse_run_directory

EXISTING_DIRECTORY = click.Path(exists=True, file_okay=False, path_type=Path, resolve_path=True)
DIRECTORY = click.Path(file_okay=False, path_type=Path, resolve_path=True)
cache_directory_option = click.option("--cache-directory", type=DIRECTORY, default=Path.home() / ".cache")
output_option = click.option("--output", type=DIRECTORY, required=True)


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--run", "forward_run", type=EXISTING_DIRECTORY, required=True)
@cache_directory_option
@output_option
def stage(forward_run: Path, cache_directory: Path, output: Path) -> None:
    try:
        report = leg(forward_run, cache_directory=cache_directory, output=output)
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(json.dumps(report))


@cli.command()
@click.option("--run", "reverse_run", type=EXISTING_DIRECTORY, required=True)
@click.option("--forward", "forward_run", type=EXISTING_DIRECTORY, required=True)
def record(reverse_run: Path, forward_run: Path) -> None:
    try:
        forward = load_run(forward_run)
        manifest = record_forward(reverse_run, run_id=forward["run_id"], condition=forward["condition"])
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(json.dumps(manifest))


@cli.command()
@click.option("--run", "forward_run", type=EXISTING_DIRECTORY, required=True)
@cache_directory_option
@output_option
def run(forward_run: Path, cache_directory: Path, output: Path) -> None:
    try:
        report = leg(forward_run, cache_directory=cache_directory, output=output)
        root = Path(report["reverse_root"])
        before = {path.name for path in root.iterdir()} if root.is_dir() else set()
        launched = subprocess.run(report["argv"])
        banked = reverse_run_directory(root, before=before)
        if banked is not None:
            record_forward(banked, **report["forward"])
    except Exception as e:
        raise click.ClickException(str(e))
    click.echo(
        json.dumps(
            {**report, "run_directory": str(banked) if banked else None, "returncode": launched.returncode}
        )
    )
    if launched.returncode:
        raise SystemExit(launched.returncode)


def leg(forward_run: Path, *, cache_directory: Path, output: Path) -> dict:
    return reverse_leg(
        forward_run,
        derivation_cache_key=derivation_cache_key,
        derivations_directory=prepared_directory(cache_directory),
        gbnf_experiment_directory=GBNF_EXPERIMENT_ROOT,
        staging_directory=staging_directory(cache_directory),
        reverse_directory=output,
    )
