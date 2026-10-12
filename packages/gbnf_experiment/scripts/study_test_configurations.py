"""Run the gbnf experiment matrix: every cell once per round, each round shuffled, until --n or Ctrl-C."""

import argparse
import json
import os
import random
import signal
import sys
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from datetime import UTC, datetime
from itertools import count, product
from pathlib import Path
from time import monotonic

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
# The approved study: 16 cells a round, 12 rounds, 192 runs.
DEFAULT_MODELS = ("claude-opus-5-5",)
DEFAULT_EFFORTS = ("medium",)
DEFAULT_ROUNDS = 12


def cells(efforts: tuple[str, ...] = DEFAULT_EFFORTS) -> list[dict]:
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
    """Round-robin: a round is every cell once, shuffled, and the next starts only after it.

    Stopped at any point, no cell is more than one run ahead of another.
    """
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


def study_test_configurations(
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
                print("Stopping: no new runs start; waiting for the in-flight runs.", file=sys.stderr)
                stopping = True
                continue
            for future in done:
                record = future.result()
                log.write(json.dumps(record) + "\n")
                log.flush()
                print(
                    f"round {record['round']} {cell_name(record['cell'])}: "
                    f"exit_code={record['exit_code']} error={record['error']}",
                    file=sys.stderr,
                )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--n", type=int, default=DEFAULT_ROUNDS, help="Rounds; 0 runs until stopped. Default: %(default)s."
    )
    parser.add_argument("--parallel", type=int, default=2, help="Default: %(default)s.")
    parser.add_argument(
        "--efforts",
        type=lambda value: tuple(value.split(",")),
        default=DEFAULT_EFFORTS,
        help="Comma-separated, e.g. low,xhigh. Default: medium.",
    )
    parser.add_argument("--models", nargs="+", choices=MODELS, default=DEFAULT_MODELS)
    parser.add_argument("--source-languages", nargs="+", choices=SOURCE_LANGUAGES)
    parser.add_argument("--cells", nargs="+", help="Cell names, as printed per run.")
    args = parser.parse_args(argv)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY is unset or empty; pass it with `uv run --env-file`.")
    selected = [
        cell
        for cell in cells(args.efforts)
        if cell["model"] in args.models
        and (not args.source_languages or cell["source_language"] in args.source_languages)
        and (not args.cells or cell_name(cell) in args.cells)
    ]
    if not selected:
        sys.exit("No cells selected.")
    settings.data_directory.mkdir(parents=True, exist_ok=True)
    out = settings.data_directory / f"matrix-{datetime.now(UTC):%Y%m%dT%H%M%SZ}.jsonl"
    print(f"{len(selected)} cells; writing {out}", file=sys.stderr)
    study_test_configurations(selected, n=args.n or None, parallel=args.parallel, api_key=api_key, out=out)


if __name__ == "__main__":
    main()
