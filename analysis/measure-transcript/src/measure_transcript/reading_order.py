from collections import Counter

# The module a caller imports: python's package `gbnf` (pyproject's package find), and the
# source of package.json's `main` and `exports["."]`; its `./builder` export is not shipped.
ENTRY_POINTS = {"python": "/input/python/gbnf/__init__.py", "javascript": "/input/javascript/src/index.ts"}
CODE_SUFFIXES = {"python": (".py",), "javascript": (".ts", ".js")}
# A glob or a shell variable left in a path names no one file.
UNEXPANDED = set("*?[$")


def reading_order(reads: list[tuple[str, str, int]], writes: int, search_calls: int, source_language: str) -> dict:
    """Where reading started, how much came before the first write into the port, and what was read again.

    `reads` is each read in order as its path, its class and the writes into
    the port made before it; `writes` is their total.
    """
    counts = Counter(path for path, _, _ in reads)
    read_order = list(dict.fromkeys(path for path, cls, _ in reads if cls == "source"))
    code = [path for path in read_order if path.endswith(CODE_SUFFIXES[source_language]) and not UNEXPANDED & set(path)]
    before = {path: cls for path, cls, written in reads if written == 0}
    most_read = counts.most_common(1)[0] if counts else (None, 1)
    return {
        "first_read_path": reads[0][0] if reads else None,
        "first_read_class": reads[0][1] if reads else None,
        "first_read_is_entry_point": code[0] == ENTRY_POINTS[source_language] if code else None,
        "files_read_before_first_write": len(before) if writes else None,
        "source_files_read_before_first_write": sum(cls == "source" for cls in before.values()) if writes else None,
        "reread_count": len(reads) - len(counts),
        "max_rereads_of_one_file": most_read[1] - 1,
        "max_rereads_path": most_read[0] if most_read[1] > 1 else None,
        "search_calls_per_file_read": search_calls / len(counts) if counts else None,
        "read_order": read_order,
        "reads_after_last_write": sum(written == writes for _, _, written in reads) if writes else None,
    }
