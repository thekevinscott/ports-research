import random

from measure_behavior.render_expression import render_expression

COMMENTS = ["# held-out grammar", "# a comment | with ::= inside", "#"]


def render_grammar(rules: dict[str, tuple], rng: random.Random) -> str:
    names = list(rules)
    if rng.random() < 0.3:
        rng.shuffle(names)
    lines = [rng.choice(COMMENTS)] if rng.random() < 0.3 else []
    for name in names:
        line = f"{name} ::= {render_expression(rules[name], rng, multiline=rng.random() < 0.3)}"
        if rng.random() < 0.2:
            line += "  " + rng.choice(COMMENTS)
        lines.append(line)
        if rng.random() < 0.2:
            lines.append("")
    text = "\n".join(lines) + "\n"
    return text.replace("\n", "\r\n") if rng.random() < 0.15 else text
