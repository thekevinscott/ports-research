import random

from measure_behavior.render_char import render_char

ATOMS = ("lit", "cls", "ref")


def render_expression(node: tuple, rng: random.Random, multiline: bool) -> str:
    def render(child: tuple) -> str:
        return render_expression(child, rng, multiline)

    def group(child: tuple) -> str:
        return ("(\n  " if multiline and rng.random() < 0.5 else "(") + render(child) + ")"

    def char(c: str) -> str:
        return render_char(c, rng, in_class=True)

    kind = node[0]
    if kind == "lit":
        return '"' + "".join(render_char(c, rng, in_class=False) for c in node[1]) + '"'
    if kind == "cls":
        items = "".join(char(item) if isinstance(item, str) else char(item[0]) + "-" + char(item[1]) for item in node[2])
        return "[" + ("^" if node[1] else "") + items + "]"
    if kind == "ref":
        return node[1]
    if kind == "seq":
        return " ".join(group(child) if child[0] == "alt" else render(child) for child in node[1])
    if kind == "alt":
        text = render(node[1][0])
        for child in node[1][1:]:
            text += (" |\n  " if multiline and rng.random() < 0.5 else " | ") + render(child)
        return text
    return (render(node[2]) if node[2][0] in ATOMS else group(node[2])) + node[1]
