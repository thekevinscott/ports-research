import json
import random
from pathlib import Path

from measure_behavior.corrupt_grammar import corrupt_grammar
from measure_behavior.generate_inputs import generate_inputs
from measure_behavior.generate_rules import generate_rules
from measure_behavior.render_grammar import render_grammar

GENERATOR_VERSION = 1
INPUTS_PER_GRAMMAR = 12
MALFORMED_INPUTS = 3
MALFORMED_SHARE = 0.2


def generate_corpus(*, out: Path, seed: int, count: int) -> None:
    rng = random.Random(seed)
    (out / "grammars").mkdir(parents=True, exist_ok=True)
    (out / "inputs").mkdir(exist_ok=True)
    for index in range(count):
        rules = generate_rules(rng)
        text = render_grammar(rules, rng)
        if rng.random() < MALFORMED_SHARE:
            text, inputs = corrupt_grammar(text, rng), generate_inputs(rules, rng, MALFORMED_INPUTS)
        else:
            inputs = generate_inputs(rules, rng, INPUTS_PER_GRAMMAR)
        (out / "grammars" / f"g{index:04d}.gbnf").write_bytes(text.encode())
        (out / "inputs" / f"g{index:04d}.json").write_text(json.dumps(inputs, ensure_ascii=False, indent=1) + "\n")
    manifest = {"seed": seed, "count": count, "generator_version": GENERATOR_VERSION}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
