"""Helpers mirroring Javascript's forgiving string indexing.

In Javascript, indexing a string out of bounds yields `undefined`, which is
falsy and can be compared against without throwing. Python raises IndexError,
so string lookups in the port go through these helpers instead.
"""


def char_at(src: str, pos: int) -> str:
    """Return the character at `pos`, or '' when out of bounds."""
    if 0 <= pos < len(src):
        return src[pos]
    return ""


def item_at(items: list, pos: int):
    """Return the item at `pos`, or None when out of bounds."""
    if 0 <= pos < len(items):
        return items[pos]
    return None
