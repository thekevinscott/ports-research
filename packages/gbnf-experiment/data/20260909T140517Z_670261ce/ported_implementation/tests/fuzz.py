"""Deterministic random grammars/inputs, used to widen the parity corpus.

Everything here is seeded, so the generated cases are stable across runs: the
fixtures recorded from the reference implementation stay valid until the seed or
the generator changes.
"""

from __future__ import annotations

import random
import string
from typing import Any, Dict, List

ALPHABET = "abcxyz012"


class Term:
    def render(self) -> str:
        raise NotImplementedError

    def sample(self, rules: Dict[str, "Rule"], rng: random.Random, depth: int) -> str:
        raise NotImplementedError


class Lit(Term):
    def __init__(self, text: str):
        self.text = text

    def render(self) -> str:
        return '"' + self.text.replace("\\", "\\\\").replace('"', '\\"') + '"'

    def sample(self, rules: Dict[str, "Rule"], rng: random.Random, depth: int) -> str:
        return self.text


class Class(Term):
    def __init__(self, members: List[Any], negated: bool = False):
        # A member is either a single character or a (start, end) range.
        self.members = members
        self.negated = negated

    def render(self) -> str:
        body = "".join(
            f"{member[0]}-{member[1]}" if isinstance(member, tuple) else member
            for member in self.members
        )
        return f"[{'^' if self.negated else ''}{body}]"

    def _chars(self) -> List[str]:
        chars: List[str] = []
        for member in self.members:
            if isinstance(member, tuple):
                chars.extend(chr(c) for c in range(ord(member[0]), ord(member[1]) + 1))
            else:
                chars.append(member)
        return chars

    def sample(self, rules: Dict[str, "Rule"], rng: random.Random, depth: int) -> str:
        chars = self._chars()
        if not self.negated:
            return rng.choice(chars)
        allowed = [c for c in string.ascii_letters + string.digits if c not in chars]
        return rng.choice(allowed)


class Ref(Term):
    def __init__(self, name: str):
        self.name = name

    def render(self) -> str:
        return self.name

    def sample(self, rules: Dict[str, "Rule"], rng: random.Random, depth: int) -> str:
        return rules[self.name].sample(rules, rng, depth + 1)


class Group(Term):
    def __init__(self, alternates: List[List[Term]]):
        self.alternates = alternates

    def render(self) -> str:
        return "(" + " | ".join(
            " ".join(term.render() for term in alternate) for alternate in self.alternates
        ) + ")"

    def sample(self, rules: Dict[str, "Rule"], rng: random.Random, depth: int) -> str:
        alternate = rng.choice(self.alternates)
        return "".join(term.sample(rules, rng, depth + 1) for term in alternate)


class Repeat(Term):
    def __init__(self, term: Term, operator: str):
        self.term = term
        self.operator = operator

    def render(self) -> str:
        return f"{self.term.render()}{self.operator}"

    def sample(self, rules: Dict[str, "Rule"], rng: random.Random, depth: int) -> str:
        counts = {"*": (0, 2), "+": (1, 2), "?": (0, 1)}[self.operator]
        return "".join(
            self.term.sample(rules, rng, depth + 1)
            for _ in range(rng.randint(*counts))
        )


class Rule:
    def __init__(self, name: str, alternates: List[List[Term]]):
        self.name = name
        self.alternates = alternates

    def render(self) -> str:
        return f"{self.name} ::= " + " | ".join(
            " ".join(term.render() for term in alternate) for alternate in self.alternates
        )

    def sample(self, rules: Dict[str, "Rule"], rng: random.Random, depth: int) -> str:
        if depth > 6:
            # Bottom out on the shortest alternate to keep sampling terminating.
            alternate = min(self.alternates, key=len)
        else:
            alternate = rng.choice(self.alternates)
        return "".join(term.sample(rules, rng, depth + 1) for term in alternate)


def _make_term(rng: random.Random, available_refs: List[str], depth: int) -> Term:
    choices = ["lit", "class", "class", "lit"]
    if available_refs:
        choices.append("ref")
    if depth < 2:
        choices.append("group")
    kind = rng.choice(choices)

    if kind == "lit":
        return Lit("".join(rng.choice(ALPHABET) for _ in range(rng.randint(1, 3))))
    if kind == "class":
        members: List[Any] = []
        for _ in range(rng.randint(1, 2)):
            if rng.random() < 0.4:
                start = rng.choice("acx")
                members.append((start, chr(ord(start) + rng.randint(1, 3))))
            else:
                members.append(rng.choice(ALPHABET))
        return Class(members, negated=rng.random() < 0.2)
    if kind == "ref":
        return Ref(rng.choice(available_refs))
    return Group(
        [
            [_make_term(rng, available_refs, depth + 1) for _ in range(rng.randint(1, 2))]
            for _ in range(rng.randint(1, 2))
        ]
    )


def _make_rule(rng: random.Random, name: str, available_refs: List[str]) -> Rule:
    alternates: List[List[Term]] = []
    for _ in range(rng.randint(1, 3)):
        terms: List[Term] = []
        for _ in range(rng.randint(1, 3)):
            term = _make_term(rng, available_refs, 0)
            if rng.random() < 0.3:
                term = Repeat(term, rng.choice("*+?"))
            terms.append(term)
        alternates.append(terms)
    return Rule(name, alternates)


def _make_grammar(rng: random.Random) -> Dict[str, Any]:
    # Rules only reference later rules, so the grammar is acyclic and samplable.
    count = rng.randint(1, 3)
    # Rule names are letters and hyphens only, per the grammar's own name syntax.
    names = ["root"] + [f"rule-{string.ascii_lowercase[i]}" for i in range(count)]
    rules: Dict[str, Rule] = {}
    for i, name in enumerate(names):
        rules[name] = _make_rule(rng, name, names[i + 1 :])
    text = "\n".join(rules[name].render() for name in names) + "\n"
    return {"text": text, "rules": rules}


def _chunk(rng: random.Random, text: str) -> List[str]:
    if not text:
        return []
    chunks: List[str] = []
    pos = 0
    while pos < len(text):
        step = rng.randint(1, 4)
        chunks.append(text[pos : pos + step])
        pos += step
    return chunks


def generate_cases(seed: int = 20240517, count: int = 60) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    cases: List[Dict[str, Any]] = []
    for i in range(count):
        grammar = _make_grammar(rng)
        sampled = grammar["rules"]["root"].sample(grammar["rules"], rng, 0)

        cases.append(
            {"name": f"fuzz-{i}-valid", "grammar": grammar["text"], "adds": _chunk(rng, sampled)}
        )
        if sampled:
            prefix = sampled[: rng.randint(0, max(0, len(sampled) - 1))]
            cases.append(
                {"name": f"fuzz-{i}-prefix", "grammar": grammar["text"], "adds": _chunk(rng, prefix)}
            )
            mutation_at = rng.randrange(len(sampled))
            mutated = (
                sampled[:mutation_at] + rng.choice("QW!~") + sampled[mutation_at + 1 :]
            )
            cases.append(
                {
                    "name": f"fuzz-{i}-mutated",
                    "grammar": grammar["text"],
                    "adds": _chunk(rng, mutated),
                }
            )
    return cases
