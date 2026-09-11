from __future__ import annotations


class GBNFError(Exception):
    """Raised when the parser hits an internal invariant violation.

    Mirrors the plain ``Error``s thrown by the reference implementation.
    """
