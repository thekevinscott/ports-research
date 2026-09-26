"""Port of ``src/rules-builder/is-word-char.ts``."""

from __future__ import annotations

import re

_WORD_CHAR = re.compile(r'[a-zA-Z]')


def is_word_char(c: str) -> bool:
    return bool(_WORD_CHAR.search(c))
