"""Types shared by the error classes.

ValidInput can either be a string, or a number indicating a code point.
It CANNOT be a number representing a number; a number intended as input
(like "8") should be passed in as a string.
"""

from __future__ import annotations

from typing import List, Union

ValidInput = Union[str, int, List[int]]
