from collections import defaultdict
from collections.abc import Sequence
from typing import Protocol


class Named(Protocol):
    name: str
    arity: int


def normalise_name(name: str) -> str:
    return name.lstrip("_#").replace("_", "").lower()


def pair_functions[F: Named](port: Sequence[F], reference: Sequence[F]) -> tuple[list[tuple[F, F]], list[F], list[F]]:
    """Pair on (normalised name, arity); functions sharing a key pair in the order given."""
    waiting = defaultdict(list)
    for fn in reference:
        waiting[normalise_name(fn.name), fn.arity].append(fn)
    pairs, port_only = [], []
    for fn in port:
        candidates = waiting[normalise_name(fn.name), fn.arity]
        if candidates:
            pairs.append((fn, candidates.pop(0)))
        else:
            port_only.append(fn)
    paired = {id(r) for _, r in pairs}
    return pairs, port_only, [fn for fn in reference if id(fn) not in paired]
