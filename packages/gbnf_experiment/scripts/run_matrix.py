"""Run the gbnf experiment matrix: every cell once per round, each round shuffled, until --n or Ctrl-C."""

import json
import os
import random
import signal
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from datetime import UTC, datetime
from itertools import count, product
from pathlib import Path
from time import monotonic

import click
from botbox import ClaudeAgent

from gbnf_experiment.condition_name import LABELS, condition_name
from gbnf_experiment.config import settings
from gbnf_experiment.prepare_filesystem.prepare_reference_implementation import (
    prepare_reference_implementation,
)
from gbnf_experiment.run_gbnf_experiment import run_gbnf_experiment

SOURCE_LANGUAGES = ("python", "javascript")
FLAGS = tuple(LABELS)
MODELS = (
    "claude-opus-5-5",
    "claude-sonnet-5-5",
    "claude-fable-5-1",
    "claude-haiku-4-5-20251001",
)


def cells(efforts: tuple[str | None, ...] = (None,)) -> list[dict]:
    """None leaves effort to the claude CLI's default."""
    return [
        {
            "source_language": source_language,
            **dict(zip(FLAGS, flags)),
            "model": model,
            "effort": effort,
        }
        for source_language, flags, model, effort in product(
            SOURCE_LANGUAGES, product((False, True), repeat=len(FLAGS)), MODELS, efforts
        )
    ]


def cell_name(cell: dict) -> str:
    """The manifest's condition name."""
    return condition_name(**cell)


def schedule(cells: list[dict], n: int | None):
    for round_number in count(1) if n is None else range(1, n + 1):
        for cell in random.sample(cells, len(cells)):
            yield round_number, cell


def run_cell(round_number: int, cell: dict, *, api_key: str) -> dict:
    start = monotonic()
    record = {
        "round": round_number,
        "cell": cell,
        "run_directory": None,
        "error": None,
        "exit_code": None,
        "usage": None,
    }
    try:
        run_directory = run_gbnf_experiment(
            agent=ClaudeAgent(model=cell["model"], effort=cell["effort"], api_key=api_key),
            source_language=cell["source_language"],
            **{flag: cell[flag] for flag in FLAGS},
            debug=False,
        )
        record["run_directory"] = str(run_directory)
        record["exit_code"] = json.loads((run_directory / "manifest.json").read_text()).get("exit_code")
        result = run_directory / "result.json"
        if result.exists():
            record["usage"] = json.loads(result.read_text()).get("usage")
    except Exception as e:
        record["error"] = str(e)
    record["wall_seconds"] = round(monotonic() - start, 1)
    return record


def ignore_interrupts() -> None:
    # Inherited by the docker subprocesses, so Ctrl-C reaches only the scheduler.
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def run_matrix(
    cells: list[dict], *, n: int | None, parallel: int, api_key: str, out: Path
) -> None:
    # Concurrent prepares of one condition collide in its shared staging directory.
    for condition in {tuple((key, cell[key]) for key in ("source_language", *FLAGS)) for cell in cells}:
        prepare_reference_implementation(**dict(condition), debug=False)
    runs = schedule(cells, n)
    stopping = False
    in_flight = set()
    with ProcessPoolExecutor(parallel, initializer=ignore_interrupts) as pool, out.open("a") as log:
        while True:
            while not stopping and len(in_flight) < parallel:
                run = next(runs, None)
                if run is None:
                    stopping = True
                else:
                    in_flight.add(pool.submit(run_cell, *run, api_key=api_key))
            if not in_flight:
                return
            try:
                done, in_flight = wait(in_flight, return_when=FIRST_COMPLETED)
            except KeyboardInterrupt:
                click.echo("Stopping: no new runs start; waiting for the in-flight runs.", err=True)
                stopping = True
                continue
            for future in done:
                record = future.result()
                log.write(json.dumps(record) + "\n")
                log.flush()
                click.echo(
                    f"round {record['round']} {cell_name(record['cell'])}: "
                    f"exit_code={record['exit_code']} error={record['error']}",
                    err=True,
                )


@click.command()
@click.option("--n", type=click.IntRange(min=1), help="Rounds. Default: until stopped.")
@click.option("--parallel", type=click.IntRange(min=1), default=2, show_default=True)
@click.option(
    "--efforts",
    callback=lambda _, __, value: tuple(value.split(",")) if value else (None,),
    help="Comma-separated, e.g. low,xhigh. Default: the claude CLI's.",
)
@click.option("--models", multiple=True, type=click.Choice(MODELS))
@click.option("--source-languages", multiple=True, type=click.Choice(SOURCE_LANGUAGES))
@click.option("--cells", "names", multiple=True, help="Cell names, as printed per run.")
def cli(
    n: int | None,
    parallel: int,
    efforts: tuple[str | None, ...],
    models: tuple[str, ...],
    source_languages: tuple[str, ...],
    names: tuple[str, ...],
) -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise click.ClickException(
            "ANTHROPIC_API_KEY is unset or empty; pass it with `uv run --env-file`."
        )
    selected = [
        cell
        for cell in cells(efforts)
        if (not models or cell["model"] in models)
        and (not source_languages or cell["source_language"] in source_languages)
        and (not names or cell_name(cell) in names)
    ]
    if not selected:
        raise click.ClickException("No cells selected.")
    settings.data_directory.mkdir(parents=True, exist_ok=True)
    out = settings.data_directory / f"matrix-{datetime.now(UTC):%Y%m%dT%H%M%SZ}.jsonl"
    click.echo(f"{len(selected)} cells; writing {out}", err=True)
    run_matrix(selected, n=n, parallel=parallel, api_key=api_key, out=out)


if __name__ == "__main__":
    cli()
