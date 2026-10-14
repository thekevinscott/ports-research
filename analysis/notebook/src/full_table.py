import marimo as mo


def full_table(frame, **kwargs):
    """A table on one page: a static export embeds only the first page of a table."""
    rows = frame.height if hasattr(frame, "height") else len(frame)
    return mo.ui.table(frame, page_size=max(1, rows), **kwargs)
