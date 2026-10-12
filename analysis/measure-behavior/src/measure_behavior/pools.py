# Characters cover ASCII, the escapes the reference parses (\t \r \n \" \\ \[ \]), the BMP and one astral code point.
CHARS = [*"abcxyzABZ019 -_.,:;!?{}()<>/'=+*|^[]", '"', "\\", "\t", "\n", "\r", "é", "ß", "λ", "中", "😀"]
RANGES = [("a", "z"), ("A", "F"), ("0", "9"), ("α", "ω"), ("一", "丏")]
# Lowercase letters and hyphens: the typescript reference rejects any other character in a name.
RULE_NAMES = ["item", "word", "digits", "tail-part", "head-part", "pair", "atom", "chunk"]
