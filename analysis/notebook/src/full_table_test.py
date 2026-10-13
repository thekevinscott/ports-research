import polars as pl

from src.full_table import full_table


def describe_full_table():
    def it_sets_the_page_size_to_the_frame_height():
        frame = pl.DataFrame({"n": list(range(48))})
        assert full_table(frame)._component_args["page-size"] == 48
