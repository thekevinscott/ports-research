import json
from pathlib import Path

from measure_behavior.run_pair import run_pair


def run_corpus(*, corpus: Path, implementation: Path, language: str, out: Path) -> None:
    # A lone surrogate (half an emoji a port sliced) cannot be utf-8; backslashreplace writes it as the JSON escape \udXXX.
    with out.open("w", encoding="utf-8", errors="backslashreplace") as records:
        for grammar_file in sorted((corpus / "grammars").glob("*.gbnf")):
            grammar = grammar_file.read_bytes().decode()
            inputs = json.loads((corpus / "inputs" / f"{grammar_file.stem}.json").read_text())
            for index, text in enumerate(inputs):
                outcome = run_pair(language, implementation, grammar, text)
                record = {"grammar": grammar_file.stem, "input": index, **outcome}
                records.write(json.dumps(record, ensure_ascii=False) + "\n")
