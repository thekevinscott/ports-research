"""The number of code points in a string.

Python strings are sequences of code points, so this is simply ``len``. The
function exists so that positions, which are code point based throughout the
library, are always counted through a single, explicit helper.
"""


def code_point_length(src: str) -> int:
    return len(src)


codePointLength = code_point_length
