"""Shared input alias, split out to keep the error helpers free of graph imports."""
from __future__ import annotations

from typing import List, Union

ValidInput = Union[str, int, List[int]]
