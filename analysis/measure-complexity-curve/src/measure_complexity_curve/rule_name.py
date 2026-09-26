import string

ALPHABET = string.ascii_lowercase


def rule_name(index: int) -> str:
    """A letter-only rule name for `index`, spreadsheet-column style (a, b, ..., z, aa, ab, ...).

    Letters only, never digits: the reference's `is_word_char` matches `[a-zA-Z]`
    only, so a digit anywhere in a name (an `r0`-style scheme) silently truncates
    the name parse instead of raising — caught by parsing a generated grammar
    against the real reference before trusting this generator.
    """
    name = ""
    index += 1
    while index > 0:
        index, remainder = divmod(index - 1, len(ALPHABET))
        name = ALPHABET[remainder] + name
    return name
