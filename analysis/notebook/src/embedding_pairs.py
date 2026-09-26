"""Compare the notebook's selected corpus using validated, existing vectors only."""

import hashlib
import json
from pathlib import Path

import numpy as np
from measure_embedding.collect_files import collect_files
from measure_embedding.compare_embeddings import compare_embeddings
from measure_embedding.embed_codebase import SUFFIXES
from measure_embedding.embedded_text import embedded_text

from src.Codebase import EMBEDDING_MODEL, EMBEDDINGS
from src.port_pairs import within_direction_pairs


def validate_cache(directory: Path, target: Path, language: str, exclude: list[str]) -> dict:
    """Check selection, stripped inputs, weights and vectors; fingerprint consumed bytes.

    Check content rather than mtimes, which can change when a cache is restored.
    Stripped sidecars attest to saved inputs; model identity comes from the cache index.
    """
    index_bytes = (directory / "index.json").read_bytes()
    index = json.loads(index_bytes)
    files = collect_files(target, suffixes=SUFFIXES[language], exclude=exclude)
    expected = [p.relative_to(target).as_posix() for p in files]
    if not expected or index["files"] != expected:
        raise ValueError(f"{directory}: cached file selection differs from source")
    if index["language"] != language or index["model"] != EMBEDDING_MODEL:
        raise ValueError(f"{directory}: cache language/model mismatch")
    if len(index["lengths"]) != len(files):
        raise ValueError(f"{directory}: missing file weights")
    digest = hashlib.sha256(index_bytes)
    for source, name, length in zip(files, expected, index["lengths"]):
        stripped = (directory / f"{name}.stripped").read_bytes()
        if stripped != embedded_text(source, language, True):
            raise ValueError(f"{directory}: stripped content differs for {name}")
        if length != len(stripped.decode(errors="replace")):
            raise ValueError(f"{directory}: incorrect weight for {name}")
        vector_path = directory / f"{name}.npy"
        vector = np.load(vector_path, allow_pickle=False)
        if (vector.shape != (index["dims"],) or not np.isfinite(vector).all()
                or np.linalg.norm(vector) == 0):
            raise ValueError(f"{directory}: invalid vector for {name}")
        digest.update(name.encode())
        digest.update(stripped)
        digest.update(vector_path.read_bytes())
    if sum(index["lengths"]) <= 0:
        raise ValueError(f"{directory}: zero total weight")
    return {"sha256": digest.hexdigest(), "file_count": len(files),
            "dims": index["dims"], "model": index["model"]}


def compare_corpus(codebases: list) -> dict:
    caches, provenance = {}, {}
    for codebase in codebases:
        for key, target, directory in (
            (codebase.run_id, codebase.path, EMBEDDINGS / "runs" / codebase.run_id),
            (f"reference-{codebase.language}", codebase.reference,
             EMBEDDINGS / "reference" / codebase.language),
        ):
            if key not in caches:
                provenance[key] = validate_cache(
                    directory, target, codebase.language, codebase.exclude
                )
                caches[key] = directory
    if len({p["dims"] for p in provenance.values()}) != 1:
        raise ValueError("Embedding dimensions differ across the corpus")

    def row(a, b=None):
        key_b = b.run_id if b else f"reference-{a.language}"
        return {
            "run_id_a": a.run_id, "run_id_b": key_b,
            "source_language": a.run["source_language"],
            "target_language": a.language,
            "comparison": "port-to-port" if b else "port-to-reference",
            **{f"{flag}_{side}": bool(c.run[flag]) if c else None
               for side, c in (("a", a), ("b", b))
               for flag in ("include_python_tests", "include_typescript_tests")},
            **compare_embeddings(a=caches[a.run_id], b=caches[key_b]),
        }

    return {
        "model": EMBEDDING_MODEL,
        "scope": "All unordered port pairs within each source/target direction; each port to its target-language reference",
        "normalization": "Comments stripped; file weights are decoded character counts",
        "cache_provenance": provenance,
        "comparisons": [row(a, b) for a, b in within_direction_pairs(codebases)]
                       + [row(a) for a in codebases],
    }
