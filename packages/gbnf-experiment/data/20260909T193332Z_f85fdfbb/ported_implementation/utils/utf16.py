"""Helpers for giving Python strings JavaScript's UTF-16 code-unit semantics.

The reference implementation indexes strings with ``[]``, measures them with
``.length`` and reads characters with ``charCodeAt`` -- all of which operate on
UTF-16 code units. Python strings are sequences of code points instead, so
astral characters (emoji, rare CJK, ...) would be counted as one character here
but two in JavaScript. Converting the source up front to a string whose
characters are each a single UTF-16 code unit keeps every offset, length and
character code identical to the reference.
"""

from __future__ import annotations

__all__ = ["to_utf16_units", "from_utf16_units", "code_units"]


def code_units(src: str) -> list[int]:
    """Return ``src`` as a list of UTF-16 code units."""
    encoded = src.encode("utf-16-le", "surrogatepass")
    return [
        int.from_bytes(encoded[i:i + 2], "little")
        for i in range(0, len(encoded), 2)
    ]


def to_utf16_units(src: str) -> str:
    """Expand astral characters into their surrogate pairs.

    The result is a string where ``len``/indexing/``ord`` match JavaScript's
    ``.length``/``[]``/``charCodeAt``.
    """
    if src.isascii():
        return src
    return "".join(chr(unit) for unit in code_units(src))


def from_utf16_units(src: str) -> str:
    """Inverse of :func:`to_utf16_units`, recombining surrogate pairs."""
    if src.isascii():
        return src
    encoded = b"".join(ord(char).to_bytes(2, "little") for char in src)
    return encoded.decode("utf-16-le", "surrogatepass")
