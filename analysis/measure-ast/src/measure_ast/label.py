def label(name: str, arity: int | None) -> str:
    return name if arity is None else f"{name}/{arity}"
