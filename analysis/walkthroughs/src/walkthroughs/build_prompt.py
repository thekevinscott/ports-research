from pathlib import Path

from judge.source_files import source_files

PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "walkthrough.md").read_text()
SUFFIXES = {"python": {".py"}, "typescript": {".ts", ".tsx", ".mts", ".cts", ".js", ".mjs", ".cjs"}}


def build_prompt(implementation: Path, language: str) -> tuple[str, list[str]]:
    """The fixed prompt, then each of the language's source files under its relative path; tests left out as in the judge's code item."""
    files = [r.as_posix() for r in source_files(implementation) if r.suffix in SUFFIXES[language]]
    code = "\n".join(f"=== {relative} ===\n{(implementation / relative).read_text(errors='replace')}" for relative in files)
    return f"{PROMPT}\n---\n\n{code}", files
