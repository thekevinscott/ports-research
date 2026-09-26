from collections.abc import Sequence
from itertools import combinations

import polars as pl

from src.Codebase import Codebase, exclude_args, run_git_diff

REFERENCE_RUN_ID = "reference"
CONDITION_FLAGS = ("include_python_tests", "include_typescript_tests")

PAIR_SCHEMA = {
    "run_id_a": pl.String,
    "run_id_b": pl.String,
    "source_language": pl.String,
    "target_language": pl.String,
    "include_python_tests_a": pl.Boolean,
    "include_typescript_tests_a": pl.Boolean,
    "include_python_tests_b": pl.Boolean,
    "include_typescript_tests_b": pl.Boolean,
    "similarity_pct": pl.Float64,
}

def direction_of(codebase: Codebase) -> tuple:
    """Source and target language, the widest group two ports can be compared inside."""
    run = codebase.run
    return (run["source_language"], run["target_language"])


def within_direction_pairs(codebases: list[Codebase]) -> list[tuple[Codebase, Codebase]]:
    directions: dict[tuple, list[Codebase]] = {}
    for codebase in codebases:
        directions.setdefault(direction_of(codebase), []).append(codebase)
    return [
        pair
        # run_git_diff caches on the two paths as given, so run id order fixes the cache key.
        for members in directions.values()
        for pair in combinations(sorted(members, key=lambda c: c.run["run_id"]), 2)
    ]


def within_direction_similarity(codebases: list[Codebase]) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "run_id_a": a.run["run_id"],
                "run_id_b": b.run["run_id"],
                "source_language": a.run["source_language"],
                "target_language": a.run["target_language"],
                "include_python_tests_a": bool(a.run["include_python_tests"]),
                "include_typescript_tests_a": bool(a.run["include_typescript_tests"]),
                "include_python_tests_b": bool(b.run["include_python_tests"]),
                "include_typescript_tests_b": bool(b.run["include_typescript_tests"]),
                "similarity_pct": run_git_diff(
                    a.path, b.path, language=a.language, exclude=exclude_args(a.exclude)
                )["similarity_pct"],
            }
            for a, b in within_direction_pairs(codebases)
        ],
        schema=PAIR_SCHEMA,
    )


def within_cell(pairs: pl.DataFrame) -> pl.DataFrame:
    """The pairs whose two ports share a condition, under the one condition they share."""
    return pairs.filter(
        pl.all_horizontal(pl.col(f"{flag}_a") == pl.col(f"{flag}_b") for flag in CONDITION_FLAGS)
    ).select(
        "run_id_a",
        "run_id_b",
        "source_language",
        "target_language",
        *(pl.col(f"{flag}_a").alias(flag) for flag in CONDITION_FLAGS),
        "similarity_pct",
    )


def label_conditions(
    pairs: pl.DataFrame, conditions: Sequence[tuple[str, bool, bool]]
) -> pl.DataFrame:
    """Each side of the pair named by the condition its own port ran under."""
    named = pl.DataFrame(
        [
            {
                CONDITION_FLAGS[0]: python_tests,
                CONDITION_FLAGS[1]: typescript_tests,
                "condition": label,
            }
            for label, python_tests, typescript_tests in conditions
        ],
        schema={
            CONDITION_FLAGS[0]: pl.Boolean,
            CONDITION_FLAGS[1]: pl.Boolean,
            "condition": pl.String,
        },
    )
    labelled = pairs
    for side in ("a", "b"):
        labelled = labelled.join(
            named.select(pl.all().name.suffix(f"_{side}")),
            on=[f"{flag}_{side}" for flag in CONDITION_FLAGS],
            how="left",
            maintain_order="left",
        )
    return labelled


SIDES = {"_a": "_b", "_b": "_a"}


def pairs_by_port(pairs: pl.DataFrame, reference: pl.DataFrame) -> pl.DataFrame:
    """Every pair once from each of its two ports, carrying that port's reference columns.

    The diff is symmetric and runs once per pair, but a chart that places a pair by one of
    its ports reads the same measurement from each end in turn.
    """
    swapped = {
        column: column[:-2] + SIDES[column[-2:]]
        for column in pairs.columns
        if column[-2:] in SIDES
    }
    both = pl.concat([pairs, pairs.rename(swapped).select(pairs.columns)])
    return both.join(
        reference.rename({"run_id": "run_id_a"}),
        on="run_id_a",
        how="inner",
        maintain_order="left",
    )
