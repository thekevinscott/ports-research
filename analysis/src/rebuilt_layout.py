"""Whether a port kept the reference's file layout, read off its reference diff columns."""

import polars as pl

# Ports land either side of a wide gap: 0 to 3 files kept at their reference path, or 25 to 35.
KEPT_FILES_FLOOR = 10
LAYOUT_KEPT = "kept the file layout"
LAYOUT_REBUILT = "rebuilt the file layout"
LAYOUT_LABELS = [LAYOUT_KEPT, LAYOUT_REBUILT]
LAYOUT_RULE = f"rebuilt: under {KEPT_FILES_FLOOR} files kept at their reference path"


def kept_files() -> pl.Expr:
    """Files the port left at the path the reference has them on, whether or not it edited them."""
    return pl.col("reference_diff_identical") + pl.col("reference_diff_modified")


def layout_flag(floor: int = KEPT_FILES_FLOOR) -> pl.Expr:
    kept = kept_files()
    return (
        pl.when(kept.is_null())
        .then(pl.lit(None, pl.String))
        .when(kept < floor)
        .then(pl.lit(LAYOUT_REBUILT))
        .otherwise(pl.lit(LAYOUT_KEPT))
        .alias("layout")
    )
