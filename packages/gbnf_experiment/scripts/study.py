"""Shared runner for the gbnf studies: every cell once per round, each round shuffled, until --n or Ctrl-C.

Stops at the first run that fails on credit or auth, naming it on stderr.
"""

import argparse
import json
import os
import random
import signal
import sys
from collections import Counter
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from datetime import UTC, datetime
from itertools import count, islice
from pathlib import Path
from time import monotonic

from botbox import ClaudeAgent
from completed_runs import CONDITION, completed_runs

from gbnf_experiment.condition_name import LABELS, condition_name
from gbnf_experiment.prepare_filesystem.prepare_reference_implementation import (
    prepare_reference_implementation,
)
from gbnf_experiment.run_gbnf_experiment import run_gbnf_experiment

SOURCE_LANGUAGES = ("python", "javascript")
FLAGS = tuple(LABELS)
DEFAULT_ROUNDS = 12
AUTH_FAILURES = ("oauth", "401", "not logged in", "authentication")


def cell_key(cell: dict) -> str:
    return json.dumps(cell, sort_keys=True)


def cell_name(cell: dict) -> str:
    """The manifest's condition name."""
    return condition_name(**cell)


def schedule(cells: list[dict], n: int | None, prior: Counter | None = None):
    """Round-robin: a round is every cell short of n successes, shuffled, and the next starts only after it.

    `prior` counts each cell's prior successes; a cell drops out once those plus its runs here reach n.
    Stopped at any point, no cell is more than one run ahead of another.
    """
    prior = prior or Counter()
    for round_number in count(1) if n is None else range(1, n + 1):
        short = [cell for cell in cells if n is None or prior[cell_key(cell)] + round_number <= n]
        for cell in random.sample(short, len(short)):
            yield round_number, cell


def prior_successes(output: Path, study: str) -> Counter:
    """Completed runs already under `output`, per cell key; they count toward --n."""
    return Counter(
        cell_key({key: bool(run[key]) if key in FLAGS else run[key] for key in CONDITION})
        for run in completed_runs(output, study)
    )


def now() -> str:
    return datetime.now(UTC).isoformat()


def run_cell(round_number: int, cell: dict, *, study: str, output: Path, api_key: str | None) -> dict:
    start = monotonic()
    record = {
        "round": round_number,
        "cell": cell,
        "run_directory": None,
        "error": None,
        "exit_code": None,
        "usage": None,
        "is_error": None,
        "terminal_reason": None,
        "result": None,
        "started_at": now(),
    }
    try:
        run_directory = run_gbnf_experiment(
            agent=ClaudeAgent(model=cell["model"], effort=cell["effort"], api_key=api_key),
            study=study,
            output=output,
            source_language=cell["source_language"],
            **{flag: cell[flag] for flag in FLAGS},
            debug=False,
        )
        record["run_directory"] = str(run_directory)
        record["exit_code"] = json.loads((run_directory / "manifest.json").read_text()).get("exit_code")
        result = run_directory / "result.json"
        if result.exists():
            result = json.loads(result.read_text())
            record["usage"] = result.get("usage")
            record["is_error"] = result.get("is_error")
            record["terminal_reason"] = result.get("terminal_reason")
            record["result"] = (result.get("result") or "")[:300]
    except Exception as e:
        record["error"] = str(e)
    record["finished_at"] = now()
    record["wall_seconds"] = round(monotonic() - start, 1)
    return record


def out_of_credit_or_auth(record: dict) -> bool:
    if record["is_error"] and record["terminal_reason"] == "api_error":
        return True
    texts = [record["result"] or "", record["error"] or ""]
    if record["run_directory"] and (stderr := Path(record["run_directory"]) / "stderr.txt").exists():
        texts.append(stderr.read_text())
    text = " ".join(texts).lower()
    return any(failure in text for failure in AUTH_FAILURES)


def ignore_interrupts() -> None:
    # Inherited by the docker subprocesses, so Ctrl-C reaches only the scheduler.
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def run_study(
    study: str,
    cells: list[dict],
    *,
    n: int | None,
    concurrency: int,
    api_key: str | None,
    log: Path,
    output: Path,
    prior: Counter | None = None,
    runs: int | None = None,
) -> dict | None:
    """Runs land in `output`, one record per run appended to `log`.

    Returns the first run that failed on credit or auth, after the in-flight runs finish.
    """
    # Concurrent prepares of one condition collide in its shared staging directory.
    for condition in {tuple((key, cell[key]) for key in ("source_language", *FLAGS)) for cell in cells}:
        prepare_reference_implementation(**dict(condition), debug=False)
    queue = islice(schedule(cells, n, prior), runs)
    stopping = False
    stopped = None
    exit_codes = Counter()
    failures = 0
    in_flight = set()
    with ProcessPoolExecutor(concurrency, initializer=ignore_interrupts) as pool, log.open("a") as records:
        while True:
            while not stopping and len(in_flight) < concurrency:
                run = next(queue, None)
                if run is None:
                    stopping = True
                else:
                    in_flight.add(pool.submit(run_cell, *run, study=study, output=output, api_key=api_key))
            if not in_flight:
                break
            try:
                done, in_flight = wait(in_flight, return_when=FIRST_COMPLETED)
            except KeyboardInterrupt:
                print("Stopping: no new runs start; waiting for the in-flight runs.", file=sys.stderr)
                stopping = True
                continue
            for future in done:
                record = future.result()
                records.write(json.dumps(record) + "\n")
                records.flush()
                print(
                    f"round {record['round']} {cell_name(record['cell'])}: "
                    f"exit_code={record['exit_code']} error={record['error']}",
                    file=sys.stderr,
                )
                exit_codes[record["exit_code"]] += 1
                if out_of_credit_or_auth(record):
                    failures += 1
                    stopping = True
                    stopped = stopped or record
    if stopped:
        print(
            f"STOPPED: round {stopped['round']} {cell_name(stopped['cell'])} "
            f"{stopped['run_directory']}: {stopped['result'] or stopped['error']}",
            file=sys.stderr,
        )
        print(
            f"{exit_codes.total()} runs; "
            + ", ".join(f"exit_code={code}: {total}" for code, total in exit_codes.items())
            + f"; credit or auth failures: {failures}",
            file=sys.stderr,
        )
    return stopped


def argument_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Directory the runs and this study's jsonl land in. No default: runs belong in the root checkout's data/runs.",
    )
    parser.add_argument(
        "--n", type=int, default=DEFAULT_ROUNDS, help="Rounds; 0 runs until stopped. Default: %(default)s."
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Concurrent jobs; each is one Docker container running the agent and its test runs. Default: %(default)s.",
    )
    parser.add_argument(
        "--auth",
        choices=("api-key", "subscription"),
        default="api-key",
        help="api-key bills ANTHROPIC_API_KEY; subscription copies the host's Claude login. Default: %(default)s.",
    )
    parser.add_argument("--runs", type=int, help="Stop submitting after this many runs. Default: unlimited.")
    return parser


def main(study: str, cells: list[dict], args: argparse.Namespace) -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if args.auth == "subscription":
        if api_key:
            sys.exit("ANTHROPIC_API_KEY is set; unset it for --auth subscription.")
        api_key = None
    elif not api_key:
        sys.exit("ANTHROPIC_API_KEY is unset or empty; pass it with `uv run --env-file`.")
    n = args.n or None
    prior = prior_successes(args.output, study)
    if n is not None:
        shortfalls = {cell_name(cell): max(n - prior[cell_key(cell)], 0) for cell in cells}
        print(
            "shortfall: " + ", ".join(f"{name}={short}" for name, short in shortfalls.items())
            + f"; total {sum(shortfalls.values())}",
            file=sys.stderr,
        )
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    log = output / f"matrix-{datetime.now(UTC):%Y%m%dT%H%M%SZ}.jsonl"
    print(f"{study}: {len(cells)} cells; auth {args.auth}; writing {log}", file=sys.stderr)
    stopped = run_study(
        study, cells, n=n, concurrency=args.concurrency, api_key=api_key, log=log, output=output, prior=prior, runs=args.runs
    )
    if stopped:
        sys.exit(1)
