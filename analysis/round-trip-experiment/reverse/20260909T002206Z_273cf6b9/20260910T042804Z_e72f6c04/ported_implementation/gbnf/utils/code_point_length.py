def code_point_length(value: str) -> int:
    """The number of code points in a string.

    Python's ``len`` already counts code points; the helper exists so that error
    rendering measures lengths in one obvious place.
    """
    return len(value)
