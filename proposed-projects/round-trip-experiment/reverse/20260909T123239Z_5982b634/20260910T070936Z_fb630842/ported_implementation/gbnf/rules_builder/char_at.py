from __future__ import annotations

from typing import Optional


def char_at(src: str, pos: int) -> Optional[str]:
    """Index into a string, returning None when out of bounds.

    The reference implementation leans on JavaScript's out-of-bounds indexing
    returning `undefined`; this keeps those comparisons expressible.
    """
    if 0 <= pos < len(src):
        return src[pos]
    return None
