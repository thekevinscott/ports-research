import tree_sitter_python as tspython
import tree_sitter_typescript as tsts
from tree_sitter import Language, Parser

PARSERS = {
    "python": Parser(Language(tspython.language())),
    "typescript": Parser(Language(tsts.language_typescript())),
}


def strip_comments(source: bytes, language: str) -> bytes:
    stack, spans = [PARSERS[language].parse(source).root_node], []
    while stack:
        node = stack.pop()
        if node.type == "comment":
            spans.append((node.start_byte, node.end_byte))
        else:
            stack.extend(node.children)
    kept, cursor = [], 0
    for start, end in sorted(spans):
        kept.append(source[cursor:start])
        cursor = end
    kept.append(source[cursor:])
    return b"".join(kept)
