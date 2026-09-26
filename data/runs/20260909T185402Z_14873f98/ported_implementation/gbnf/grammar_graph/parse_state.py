import json


class ParseState:
    """An immutable view of the parse: the rules that may come next.

    Iterate it for the possible rules, and `add` (or `+`) input to advance it.
    """

    def __init__(self, graph, pointers):
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input_: str) -> "ParseState":
        return self.add(input_)

    def __iter__(self):
        return self.rules()

    def rules(self):
        seen: set[str] = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = json.dumps(rule.__dict__, separators=(",", ":"))
            if key not in seen:
                seen.add(key)
                yield rule

    def add(self, input_: str) -> "ParseState":
        pointers = self._graph.add(input_, self._pointers)
        return ParseState(self._graph, pointers)

    def __add__(self, input_: str) -> "ParseState":
        return self.add(input_)

    @property
    def size(self) -> int:
        return len(list(self.rules()))

    def __len__(self) -> int:
        return self.size

    def __bool__(self) -> bool:
        return True

    @property
    def grammar(self) -> str:
        return self._graph.grammar

    def __repr__(self) -> str:
        return f"ParseState({list(self.rules())!r})"
