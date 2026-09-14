import json
import os
import subprocess
from pathlib import Path

import click
from gbnf_experiment.config import PACKAGE_ROOT as GBNF_EXPERIMENT_ROOT, derivation_cache_key, settings as gbnf_settings

from .config import settings
from .load_run import load_run
from .record_forward import record_forward
from .reverse_leg import reverse_leg
from .reverse_run_directory import reverse_run_directory

EXISTING_DIRECTORY = click.Path(exists=True, file_okay=False, path_type=Path, resolve_path=True)


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--run", "forward_run", type=EXISTING_DIRECTORY, required=True)
def stage(forward_run: Path) -> None:
    try:
        report = leg(forward_run)
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
def run(forward_run: Path) -> None:
    try:
        report = leg(forward_run)
        root = Path(report["reverse_root"])
        before = {path.name for path in root.iterdir()} if root.is_dir() else set()
        launched = subprocess.run(report["argv"], env={**os.environ, **report["env"]})
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


def leg(forward_run: Path) -> dict:
    return reverse_leg(
        forward_run,
        derivation_cache_key=derivation_cache_key,
        derivations_directory=gbnf_settings.derivations_directory,
        gbnf_experiment_directory=GBNF_EXPERIMENT_ROOT,
        staging_directory=settings.staging_directory,
        reverse_directory=settings.reverse_directory,
    )
