import json
from pathlib import Path


def fixture_cases(grammars_dir: Path) -> list[dict]:
    grammar_paths = sorted(grammars_dir.glob("*.gbnf"))
    if not grammar_paths:
        raise FileNotFoundError(f"no *.gbnf fixtures under {grammars_dir}")
    return [
        {"grammar": grammar_path.read_text(), "input": text}
        for grammar_path in grammar_paths
        for text in json.loads(grammar_path.with_suffix(".json").read_text())
    ]
