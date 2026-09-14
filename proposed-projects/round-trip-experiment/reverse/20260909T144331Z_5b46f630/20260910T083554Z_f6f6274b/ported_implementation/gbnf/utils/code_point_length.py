# Python strings are sequences of code points, so the code point length of a string is simply
# its length. The helper exists to mirror the reference implementation, where positions
# reported by the parser are code point offsets and have to be counted explicitly.
def code_point_length(src: str) -> int:
    return len(src)
