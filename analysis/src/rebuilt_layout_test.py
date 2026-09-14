import polars as pl

from src.rebuilt_layout import (
    KEPT_FILES_FLOOR,
    LAYOUT_KEPT,
    LAYOUT_LABELS,
    LAYOUT_REBUILT,
    LAYOUT_RULE,
    layout_flag,
)

SCHEMA = {"reference_diff_identical": pl.Int64, "reference_diff_modified": pl.Int64}


def labels(identical, modified, **kwargs):
    frame = pl.DataFrame(
        {"reference_diff_identical": identical, "reference_diff_modified": modified},
        schema=SCHEMA,
    )
    return frame.with_columns(layout_flag(**kwargs))["layout"].to_list()


def describe_layout_flag():
    def it_flags_a_port_that_kept_almost_no_file_at_its_reference_path():
        assert labels([0], [1]) == [LAYOUT_REBUILT]

    def it_leaves_a_port_that_kept_the_layout_unflagged():
        assert labels([1], [28]) == [LAYOUT_KEPT]

    def it_counts_identical_and_modified_files_together():
        assert labels([KEPT_FILES_FLOOR - 1], [1]) == [LAYOUT_KEPT]

    def it_reads_the_floor_as_the_first_kept_count():
        assert labels([0], [KEPT_FILES_FLOOR]) == [LAYOUT_KEPT]
        assert labels([0], [KEPT_FILES_FLOOR - 1]) == [LAYOUT_REBUILT]

    def it_takes_a_floor_of_its_own():
        assert labels([0], [12], floor=20) == [LAYOUT_REBUILT]

    def it_labels_every_row_of_a_frame():
        assert labels([0, 1], [2, 28]) == [LAYOUT_REBUILT, LAYOUT_KEPT]

    def it_leaves_a_run_with_no_reference_diff_unlabelled():
        assert labels([None], [None]) == [None]


def describe_layout_labels():
    def it_orders_the_kept_label_before_the_rebuilt_one():
        assert LAYOUT_LABELS == [LAYOUT_KEPT, LAYOUT_REBUILT]

    def it_states_the_floor_in_the_rule():
        assert str(KEPT_FILES_FLOOR) in LAYOUT_RULE
