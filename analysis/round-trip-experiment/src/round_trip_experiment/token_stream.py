from collections.abc import Iterator

from tree_sitter import Node, Parser

from .languages import LanguageSpec

PLACEHOLDER = "ID"
COMMENT = "comment"


def leaves(root: Node) -> Iterator[Node]:
    stack = [root]
    while stack:
        node = stack.pop()
        if node.child_count == 0:
            yield node
        stack.extend(reversed(node.children))


def token_stream(source: bytes, parser: Parser, spec: LanguageSpec, *, abstract_identifiers: bool) -> list[str]:
    return [
        PLACEHOLDER if abstract_identifiers and leaf.type in spec.identifiers else leaf.text.decode(errors="replace")
        for leaf in leaves(parser.parse(source).root_node)
        if leaf.type != COMMENT and leaf.text
    ]
