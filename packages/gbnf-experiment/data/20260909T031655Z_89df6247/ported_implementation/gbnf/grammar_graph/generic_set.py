class GenericSet:
    """A set keyed by a derived value; first element to claim a key wins."""

    def __init__(self, get_key):
        self.get_key = get_key
        self._keys: dict = {}

    def add(self, el) -> None:
        key = self.get_key(el)
        if key not in self._keys:
            self._keys[key] = el

    def delete(self, el) -> None:
        key = self.get_key(el)
        if key not in self._keys:
            raise Exception("Could not get ref")
        del self._keys[key]

    def has(self, el) -> bool:
        return any(existing is el for existing in self._keys.values())

    def get(self, el):
        return self._keys.get(self.get_key(el))

    def __iter__(self):
        return iter(list(self._keys.values()))

    @property
    def size(self) -> int:
        return len(self._keys)
