def is_nullable(node: tuple, rules: dict[str, tuple]) -> bool:
    kind = node[0]
    if kind == "ref":
        return is_nullable(rules[node[1]], rules)
    if kind == "seq":
        return all(is_nullable(child, rules) for child in node[1])
    if kind == "alt":
        return any(is_nullable(child, rules) for child in node[1])
    if kind == "rep":
        return node[1] in "*?" or is_nullable(node[2], rules)
    return False
