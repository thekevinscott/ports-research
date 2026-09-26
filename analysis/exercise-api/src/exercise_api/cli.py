import json
from pathlib import Path

import click

from .exercise_api import exercise_api
from .fixture_cases import fixture_cases
from .generate_cases import generate_cases
from .ladder_cases import ladder_cases
from .read_cases import read_cases
from .write_cases import write_cases
from .write_report import write_report

DIRECTORY = click.Path(exists=True, file_okay=False, path_type=Path, resolve_path=True)
OUT = click.Path(dir_okay=False, path_type=Path)
DEFAULT_MEMORY_LIMIT_BYTES = {"python": 4 * 1024**3, "typescript": 28 * 1024**3}


@click.group(invoke_without_command=True)
@click.option("--language", type=click.Choice(["python", "typescript"]))
@click.option("--reference", type=DIRECTORY, help="Root of the reference implementation.")
@click.option("--target", "targets", type=DIRECTORY, multiple=True, help="Root of a port, repeatable.")
@click.option("--cases", type=click.Path(exists=True, dir_okay=False, path_type=Path), help="JSONL of {grammar, input}.")
@click.option("--adapt", is_flag=True, help="Load targets through execute-test-suite's shim rules.")
@click.option("--timeout", type=float, default=600.0, show_default=True, help="Seconds allowed per driver run.")
@click.option("--repeat", type=int, default=1, show_default=True, help="Timed passes over the case list; above 1 the report carries per-phase timings.")
@click.option("--warmup", type=int, default=0, show_default=True, help="Untimed passes over the case list before the timed ones.")
@click.option(
    "--memory-limit-bytes", type=int, help="Address-space cap per driver process [default: 4 GiB python, 28 GiB typescript]."
)
@click.option("--out", type=OUT, help="Write the report here; <out>.partial.json holds the finished targets until then.")
@click.pass_context
def cli(ctx, language, reference, targets, cases, adapt, timeout, repeat, warmup, memory_limit_bytes, out) -> None:
    if ctx.invoked_subcommand is not None:
        return
    missing = [name for name, value in [("--language", language), ("--reference", reference), ("--target", targets), ("--cases", cases)] if not value]
    if missing:
        raise click.UsageError(f"missing required option(s): {', '.join(missing)}")
    partial = out.with_suffix(".partial.json") if out else None

    def checkpoint(report: dict) -> None:
        if partial:
            write_report(partial, report)

    try:
        report = exercise_api(
            language=language,
            reference=reference,
            targets=list(targets),
            cases=read_cases(cases),
            adapt=adapt,
            timeout=timeout,
            repeat=repeat,
            warmup=warmup,
            memory_limit_bytes=memory_limit_bytes or DEFAULT_MEMORY_LIMIT_BYTES[language],
            checkpoint=checkpoint,
        )
    except Exception as e:
        raise click.ClickException(str(e))
    if out:
        write_report(out, report)
        partial.unlink(missing_ok=True)
    click.echo(json.dumps(report))


@cli.command()
@click.option("--seed", type=int, default=0, show_default=True)
@click.option("--count", type=int, default=500, show_default=True)
@click.option("--out", type=OUT, required=True)
def generate(seed: int, count: int, out: Path) -> None:
    write_cases(generate_cases(seed=seed, count=count), out)


@cli.command()
@click.option("--grammars", type=DIRECTORY, required=True, help="Directory of paired *.gbnf and *.json fixtures.")
@click.option("--out", type=OUT, required=True)
def fixtures(grammars: Path, out: Path) -> None:
    write_cases(fixture_cases(grammars), out)


@cli.command()
@click.option("--grammars", type=DIRECTORY, required=True, help="Directory of paired *.gbnf and *.json fixtures.")
@click.option("--out", type=OUT, required=True)
def ladder(grammars: Path, out: Path) -> None:
    write_cases(ladder_cases(grammars), out)
