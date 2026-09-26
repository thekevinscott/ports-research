"""Valid input can either be a string, a number indicating a code point, or a
list of code points.
"""

from typing import List, Union

ValidInput = Union[str, int, List[int]]
