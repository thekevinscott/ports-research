"""Indexing helper.

JavaScript returns ``undefined`` for an out-of-range string index, and the
reference implementation leans on that heavily (``src[pos] === '"'``,
``if (src[pos])``). Python raises instead, so every such read goes through this
helper, which yields the empty string — falsy, and equal to no character.
"""

from __future__ import annotations


def char_at(src: str, pos: int) -> str:
    if 0 <= pos < len(src):
        return src[pos]
    return ''
