import json


class ParseState:
    def __init__(self, graph, pointers):
        self._graph = graph
        self._pointers = pointers

    def __call__(self, input_: str) -> "ParseState":
        return self.add(input_)

    def __iter__(self):
        return self.rules()

    def rules(self):
        rules = set()
        for pointer in self._pointers:
            rule = pointer.rule
            key = json.dumps(rule.__dict__)
            if key not in rules:
                rules.add(key)
                yield rule

    def add(self, input_: str) -> "ParseState":
        pointers = self._graph.add(input_, self._pointers)
        return ParseState(self._graph, pointers)

    def __add__(self, input_: str) -> "ParseState":
        return self.add(input_)

    def __bool__(self) -> bool:
        return True

    @property
    def size(self) -> int:
        return len(list(self.rules()))

    @property
    def grammar(self) -> str:
        return self._graph.grammar

    def __repr__(self) -> str:
        return f"ParseState({list(self.rules())!r})"
