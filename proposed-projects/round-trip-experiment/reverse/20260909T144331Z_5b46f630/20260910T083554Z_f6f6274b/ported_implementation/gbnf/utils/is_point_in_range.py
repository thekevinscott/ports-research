from typing import List, Sequence, Union

Range = Union[List[int], Sequence[int]]


def is_point_in_range(point: int, given_range: Range) -> bool:
    if not isinstance(point, int) or isinstance(point, bool):
        raise ValueError("point must be an integer")
    return given_range[0] <= point <= given_range[1]
