def _render_item(item) -> str:
    match item:
        case ("literal", text):
            return f'"{text}"'
        case ("class", negate, members):
            body = "".join(f"{lo}-{hi}" if isinstance(m, tuple) else m for (m, lo, hi) in ((m, *(m if isinstance(m, tuple) else (m, m))) for m in members))
            return f"[{'^' if negate else ''}{body}]"
        case ("ref", name):
            return name
        case ("group", alternatives):
            return f"({_render_alternatives(alternatives)})"
        case ("repeat", inner, op):
            return f"{_render_item(inner)}{op}"
    raise ValueError(f"unknown item {item!r}")


def _render_alternatives(alternatives) -> str:
    return " | ".join(" ".join(_render_item(item) for item in sequence) for sequence in alternatives)


def render_grammar(rules: list[tuple]) -> str:
    return "\n".join(f"{name} ::= {_render_alternatives(alternatives)}" for name, alternatives in rules)
