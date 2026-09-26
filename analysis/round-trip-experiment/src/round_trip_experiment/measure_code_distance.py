from pathlib import Path

from rapidfuzz.distance import Levenshtein

from .collect_files import collect_files
from .languages import LANGUAGES, LanguageSpec
from .token_stream import token_stream


def read_codebase(language: str, target: Path, spec: LanguageSpec, exclude: list[str]) -> dict:
    files = collect_files(target, suffixes=spec.parsers, exclude=exclude)
    if not files:
        raise FileNotFoundError(f"no {language} source files under {target}")
    sources = [(path.read_bytes(), spec.parsers[path.suffix]) for path in files]
    return {
        "file_count": len(files),
        "paths": [p.relative_to(target).as_posix() for p in collect_files(target, exclude=exclude)],
        "tokens": [t for source, parser in sources for t in token_stream(source, parser, spec, abstract_identifiers=True)],
        "raw_tokens": [t for source, parser in sources for t in token_stream(source, parser, spec, abstract_identifiers=False)],
        "text": "".join(source.decode(errors="replace") for source, _ in sources),
    }


def measure_code_distance(*, language: str, a: Path, b: Path, exclude: list[str]) -> dict:
    spec = LANGUAGES[language]
    codebase_a = read_codebase(language, a, spec, exclude)
    codebase_b = read_codebase(language, b, spec, exclude)
    return {
        "language": language,
        "a": str(a),
        "b": str(b),
        "file_count_a": codebase_a["file_count"],
        "file_count_b": codebase_b["file_count"],
        "token_count_a": len(codebase_a["tokens"]),
        "token_count_b": len(codebase_b["tokens"]),
        "char_count_a": len(codebase_a["text"]),
        "char_count_b": len(codebase_b["text"]),
        "token_levenshtein": Levenshtein.normalized_distance(codebase_a["tokens"], codebase_b["tokens"]),
        "token_levenshtein_raw": Levenshtein.normalized_distance(codebase_a["raw_tokens"], codebase_b["raw_tokens"]),
        "char_levenshtein": Levenshtein.normalized_distance(codebase_a["text"], codebase_b["text"]),
        "path_count_a": len(codebase_a["paths"]),
        "path_count_b": len(codebase_b["paths"]),
        "path_levenshtein": Levenshtein.normalized_distance(codebase_a["paths"], codebase_b["paths"]),
    }
